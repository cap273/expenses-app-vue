<template>
  <div class="page-background">
    <v-container class="content-container">
        <!-- Chart Component -->
        <div class="content-box">
          <expense-chart :expenses="processedExpenses" />
        </div>

        <div class="content-box">
          <div class="search-add-container">
            <v-btn
              color="primary"
              @click="toggleAddExpense"
              class="mr-2 circle-btn"
              width="0"
            >
              <v-icon :class="{'rotate-icon': showAddExpense}">
                  mdi-plus
              </v-icon>
            </v-btn>
            <v-text-field
              v-model="search"
              label="Search"
              class="search-bar"
              outlined
              dense
              hide-details="auto"
              style="margin-bottom:0; margin-left:20px"
            ></v-text-field>
            
          <!-- Action Buttons -->
            <v-btn-group v-if="selected.length > 0" style="margin-left:20px;">
              <v-btn color="warning" @click="openBulkEditDialog" variant="outlined">
                <v-icon left>mdi-pencil-multiple</v-icon>
                Bulk Edit
              </v-btn>
              <v-btn color="error" @click="deleteSelectedExpenses">
                <v-icon left>mdi-trash-can</v-icon>
              </v-btn>
            </v-btn-group>
          </div>
          
          <!-- Add Expense Form -->
          <div v-if="showAddExpense">
            <input-expenses @update-expenses="handleUpdateExpenses" />
          </div>

          <!-- Loading Screen -->
          <div v-if="loading" class="text-center">
            <v-progress-circular indeterminate></v-progress-circular>
          </div>

          <!-- Month Headers -->
          <div v-if="!loading && monthGroups.length > 0">
            <div v-for="(group, index) in monthGroups" :key="group.month">
              <div class="month-header" @click="toggleMonthGroup(index)">
                <v-icon>{{ group.isOpen ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                <span class="month-name">{{ group.month }}</span>
                <v-chip size="small" color="primary" variant="tonal" class="ml-2">
                  {{ formatCurrency(group.total) }}
                </v-chip>
              </div>
              
              <v-data-table
                v-show="group.isOpen"
                :headers="headers"
                :items="group.expenses"
                :search="search"
                class="elevation-1 expense-table mb-4"
                item-value="ExpenseID"
                density="compact"
                :no-data-text="'No expenses found'"
                :items-per-page="-1"
                show-select
                v-model:selected="selected"
                :hide-default-header="index > 0"
                hover
              >
                <!-- Source Field (Bank Account) -->
                <template v-slot:item.Source="{ item }">
                  <div v-if="item.PlaidAccountID" class="account-info">
                    <v-avatar size="24" class="mr-2" v-if="item.PlaidMerchantLogoURL">
                      <v-img :src="item.PlaidMerchantLogoURL" alt="Bank Logo"></v-img>
                    </v-avatar>
                    <v-tooltip location="top">
                      <template v-slot:activator="{ props }">
                        <span v-bind="props" class="bank-name">
                          {{ getBankName(item.PlaidAccountID) }}
                        </span>
                      </template>
                      <span>{{ getBankAccountDetails(item.PlaidAccountID) }}</span>
                    </v-tooltip>
                  </div>
                  <div v-else>
                    <v-icon small>mdi-pencil-box-outline</v-icon>
                    <span class="account-manual">Manual</span>
                  </div>
                </template>

                <!-- Scope Name Column -->
                <template v-slot:item.ScopeName="{ item }">
                  {{ item.ScopeName }} 
                  <v-chip size="x-small" :color="item.ScopeType === 'personal' ? 'blue' : 'purple'" class="ml-1" variant="flat">
                    {{ item.ScopeType.charAt(0).toUpperCase() }}
                  </v-chip>
                </template>

                <!-- Expense Date Column -->
                <template v-slot:item.ExpenseDate="{ item }">
                  {{ formatDate(item.ExpenseDate) }}
                </template>

                <!-- Category Column with Icons for Plaid Transactions -->
                <template v-slot:item.ExpenseCategory="{ item }">
                  <div class="category-cell">
                    <span>{{ item.ExpenseCategory || getPlaidCategory(item) }}</span>
                    <v-icon 
                      v-if="item.PlaidPersonalFinanceCategoryPrimary" 
                      size="small" 
                      color="green" 
                      class="ml-2"
                      title="Auto-categorized"
                    >
                      mdi-robot
                    </v-icon>
                  </div>
                </template>

                <!-- Actions Column -->
                <template v-slot:item.actions="{ item }">
                  <div class="action-buttons">
                    <v-btn
                      icon="mdi-pencil"
                      size="small"
                      variant="text"
                      color="grey-darken-1"
                      class="me-2 action-button"
                      @click="editExpense(item)"
                    ></v-btn>
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="grey-darken-1"
                      class="action-button"
                      @click="deleteExpense(item.ExpenseID)"
                    ></v-btn>
                  </div>
                </template>
              </v-data-table>
            </div>
          </div>
        </div>

        <!-- Edit Expense Dialog -->
        <v-dialog v-model="isEditDialogOpen" max-width="1200px">
          <template v-slot:default="dialog">
            <v-card>
              <v-toolbar color="primary" dark>
                <v-toolbar-title>Edit Expense</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon @click="isEditDialogOpen = false">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-toolbar>
              <v-card-text>
                <input-expenses
                  :expenseData="selectedExpense"
                  @update-expenses="handleUpdateExpenses"
                />
              </v-card-text>
            </v-card>
          </template>
        </v-dialog>

        <!-- Bulk Edit Dialog -->
        <v-dialog v-model="isBulkEditDialogOpen" max-width="800px">
          <v-card>
            <v-card-title class="headline">
              Bulk Edit {{ selected.length }} Expenses
            </v-card-title>
            <v-card-text>
              <v-alert type="info" variant="tonal" class="mb-4">
                Choose which fields to update. Only selected fields will be changed.
              </v-alert>
              
              <!-- Edit Fields -->
              <v-row>
                <v-col cols="12" sm="6">
                  <v-checkbox v-model="bulkEdit.updateCategory" label="Update Category"></v-checkbox>
                  <v-select
                    v-if="bulkEdit.updateCategory"
                    v-model="bulkEdit.category"
                    :items="categories"
                    label="New Category"
                    class="ml-4"
                  ></v-select>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-checkbox v-model="bulkEdit.updateScope" label="Update Scope"></v-checkbox>
                  <v-select
                    v-if="bulkEdit.updateScope"
                    v-model="bulkEdit.scope"
                    :items="scopes"
                    item-title="name"
                    item-value="id"
                    label="New Scope"
                    class="ml-4"
                  ></v-select>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-checkbox v-model="bulkEdit.updateDate" label="Update Date"></v-checkbox>
                  <v-row v-if="bulkEdit.updateDate" class="ml-2">
                    <v-col cols="4">
                      <v-text-field
                        v-model="bulkEdit.day"
                        label="Day"
                        type="number"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="4">
                      <v-select
                        v-model="bulkEdit.month"
                        :items="months"
                        label="Month"
                      ></v-select>
                    </v-col>
                    <v-col cols="4">
                      <v-text-field
                        v-model="bulkEdit.year"
                        label="Year"
                        type="number"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-checkbox v-model="bulkEdit.updateNotes" label="Update Notes"></v-checkbox>
                  <v-text-field
                    v-if="bulkEdit.updateNotes"
                    v-model="bulkEdit.notes"
                    label="New Notes"
                    class="ml-4"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey" text @click="isBulkEditDialogOpen = false">Cancel</v-btn>
              <v-btn
                color="warning"
                @click="applyBulkEdit"
                :disabled="!isBulkEditValid"
                :loading="bulkEditLoading"
              >
                Apply to {{ selected.length }} Expenses
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
    </v-container>
  </div>
</template>

<style scoped>
.search-add-container {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  border-radius: 8px;
}

.search-bar {
  flex-grow: 1;
  background-color: var(--v-surface-variant-color);
}

.v-icon {
  transition: transform 0.3s ease; /* Apply transition to all rotations */
}

/* Rotate icon when the form is toggled open */
.rotate-icon {
  transform: rotate(135deg); /* Rotate 45 degrees */
}

/* Circular button styling */
.circle-btn {
  height: 64px;
  border-radius: 50%; /* Make the button round */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Add hover effects for the action buttons */
.v-btn.v-btn--icon {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.v-btn.v-btn--icon:hover {
  opacity: 1;
}

/* Style the table rows and action buttons */
.expense-table :deep(.v-data-table__tr) {
  transition: background-color 0.2s ease;
}

.expense-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(0, 0, 0, 0.03);
}

/* Hide action buttons by default */
.action-buttons {
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
}

/* Show action buttons on row hover */
.expense-table :deep(.v-data-table__tr:hover) .action-buttons {
  opacity: 1;
}

/* Action buttons */
.action-button {
  opacity: 0.7;
  transition: opacity 0.2s ease, background-color 0.2s ease;
  color: rgb(var(--v-theme-on-surface)) !important;
}

.action-button:hover {
  opacity: 1;
  background-color: var(--v-surface-variant-color);
}

/* Month header styling */
.month-header {
  background-color: var(--v-surface-variant-color);
  border-radius: 4px;
  padding: 10px 16px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.month-header:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.month-name {
  font-weight: 600;
  margin-left: 8px;
}

/* Account info styling */
.account-info {
  display: flex;
  align-items: center;
}

.bank-name {
  font-size: 0.875rem;
  text-decoration: underline;
  text-decoration-style: dotted;
  cursor: help;
}

.account-manual {
  font-size: 0.875rem;
  color: rgb(var(--v-theme-on-surface));
  opacity: 0.7;
  margin-left: 4px;
}

/* Category cell */
.category-cell {
  display: flex;
  align-items: center;
}
</style>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import InputExpenses from './InputExpenses.vue';
import ExpenseChart from './ExpenseCharts.vue';
import { formatDate } from '@/utils/dateUtils.js';


export default {
  components: {
    InputExpenses,
    ExpenseChart,
  },
  setup() {
    const loading = ref(true);
    const search = ref("");
    const expenses = ref([]);
    const headers = ref([
      { title: 'Source', value: 'Source', sortable: true },
      { title: 'Scope', value: 'ScopeName', sortable: true },
      { title: 'Date', value: 'ExpenseDate', sortable: true },
      { title: 'Amount', value: 'Amount' },
      { title: 'Category', value: 'ExpenseCategory', sortable: true },
      { title: 'Notes', value: 'AdditionalNotes', sortable: true },
      { title: 'Actions', value: 'actions', sortable: false },
    ]);

    const selected = ref([]);
    const plaidAccounts = ref({});
    const categories = ref([]);
    const scopes = ref([]);
    const monthGroups = ref([]);

    // Initialize bulk edit state
    const isBulkEditDialogOpen = ref(false);
    const bulkEditLoading = ref(false);
    const bulkEdit = ref({
      updateCategory: false,
      category: '',
      updateScope: false,
      scope: '',
      updateDate: false,
      day: '',
      month: '',
      year: '',
      updateNotes: false,
      notes: ''
    });

    // Months array for the bulk edit form
    const months = ref(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']);

    // Check if bulk edit form is valid
    const isBulkEditValid = computed(() => {
      if (!bulkEdit.value.updateCategory && 
          !bulkEdit.value.updateScope && 
          !bulkEdit.value.updateDate && 
          !bulkEdit.value.updateNotes) {
        return false;
      }
      
      if (bulkEdit.value.updateCategory && !bulkEdit.value.category) {
        return false;
      }
      
      if (bulkEdit.value.updateScope && !bulkEdit.value.scope) {
        return false;
      }
      
      if (bulkEdit.value.updateDate) {
        if (!bulkEdit.value.day || !bulkEdit.value.month || !bulkEdit.value.year) {
          return false;
        }
        
        // Validate date values
        const day = parseInt(bulkEdit.value.day);
        const year = parseInt(bulkEdit.value.year);
        
        if (isNaN(day) || day < 1 || day > 31) {
          return false;
        }
        
        if (isNaN(year) || year < 2000 || year > 2050) {
          return false;
        }
      }
      
      if (bulkEdit.value.updateNotes && bulkEdit.value.notes === '') {
        return false;
      }
      
      return true;
    });

    // Group expenses by month
    const updateMonthGroups = () => {
      const groupedExpenses = {};
      
      // First, create a sorted array of processed expenses
      const sortedExpenses = [...processedExpenses.value].sort((a, b) => {
        // For date sorting, convert to Date objects
        const dateA = new Date(a.ExpenseDate);
        const dateB = new Date(b.ExpenseDate);
        return dateB - dateA; // Newest first
      });
      
      // Group by month and year
      sortedExpenses.forEach((expense) => {
        const month = expense.ExpenseMonth;
        if (!groupedExpenses[month]) {
          groupedExpenses[month] = {
            month,
            expenses: [],
            total: 0,
            isOpen: true // Default to open
          };
        }
        
        // Add to group
        groupedExpenses[month].expenses.push(expense);
        
        // Add to total
        const amount = parseFloat(expense.Amount?.toString().replace(/[^0-9.-]+/g, "") || 0);
        groupedExpenses[month].total += amount;
      });
      
      // Convert to array and sort by date (newest first)
      monthGroups.value = Object.values(groupedExpenses).sort((a, b) => {
        // Extract year and month for comparison
        const [monthA, yearA] = a.month.split(' ');
        const [monthB, yearB] = b.month.split(' ');
        
        // Compare years first
        if (yearA !== yearB) {
          return parseInt(yearB) - parseInt(yearA);
        }
        
        // If years are the same, compare months
        const monthIndex = (m) => months.value.findIndex(month => month === m);
        return monthIndex(monthB) - monthIndex(monthA);
      });
    };

    // Toggle month group visibility
    const toggleMonthGroup = (index) => {
      monthGroups.value[index].isOpen = !monthGroups.value[index].isOpen;
    };

    // Format currency
    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount);
    };

    // Fetch Plaid accounts data
    const fetchPlaidAccounts = async () => {
      try {
        const response = await fetch('/api/get_plaid_items');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.items) {
            // Process items to get account details
            for (const item of data.items) {
              try {
                const accountsResponse = await fetch(`/api/get_item_accounts?item_id=${item.item_id}`);
                if (accountsResponse.ok) {
                  const accountsData = await accountsResponse.json();
                  if (accountsData.success && accountsData.accounts) {
                    // Store account details by account_id
                    accountsData.accounts.forEach(account => {
                      plaidAccounts.value[account.account_id] = {
                        name: account.name,
                        official_name: account.official_name,
                        mask: account.mask,
                        subtype: account.subtype,
                        type: account.type,
                        institution: item.institution_name
                      };
                    });
                  }
                }
              } catch (e) {
                console.error(`Error fetching accounts for item ${item.item_id}:`, e);
              }
            }
          }
        }
      } catch (e) {
        console.error('Error fetching Plaid items:', e);
      }
    };

    // Fetch categories for bulk edit
    const fetchCategories = async () => {
      try {
        const response = await fetch('/api/get_categories');
        if (response.ok) {
          const data = await response.json();
          categories.value = data.categories || [];
        }
      } catch (e) {
        console.error('Error fetching categories:', e);
      }
    };

    // Fetch scopes for bulk edit
    const fetchScopes = async () => {
      try {
        const response = await fetch('/api/get_scopes');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.scopes) {
            scopes.value = data.scopes.map(scope => ({
              id: scope.id,
              name: `${scope.name} (${scope.type})`
            }));
          }
        }
      } catch (e) {
        console.error('Error fetching scopes:', e);
      }
    };

    const fetchExpenses = async () => {
      loading.value = true;
      try {
        const response = await fetch('/api/get_expenses');
        if (!response.ok) throw new Error('Failed to fetch expenses');

        const data = await response.json();
        console.log('API Response:', data);

        if (data.success) {
          expenses.value = data.expenses;
          console.log('Expenses fetched:', expenses.value);
          // Update month groups after fetching expenses
          updateMonthGroups();
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        loading.value = false;
      }
    };

    const deleteExpense = async (expenseId) => {
      try {
        const response = await fetch("/api/delete_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ expenseIds: [expenseId] }),
        });

        if (!response.ok) {
          throw new Error("Failed to delete expense");
        }

        const data = await response.json();
        if (data.success) {
          // Remove the deleted expense from the list
          expenses.value = expenses.value.filter(
            expense => expense.ExpenseID !== expenseId
          );
          // Update month groups
          updateMonthGroups();
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    const deleteSelectedExpenses = async () => {
      if (selected.value.length === 0) {
        console.log("No expenses selected");
        return;
      }

      console.log("Selected Expense IDs:", selected.value.map(item => item.ExpenseID)); 

      try {
        const selectedIds = selected.value.map(expense => expense.ExpenseID);
        const body = JSON.stringify({ expenseIds: selectedIds });

        const response = await fetch("/api/delete_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
        });

        if (!response.ok) {
          throw new Error("Failed to delete expenses");
        }

        const data = await response.json();
        if (data.success) {
          // Remove deleted expenses from the list based on ExpenseID
          expenses.value = expenses.value.filter(
            expense => !selectedIds.includes(expense.ExpenseID)
          );
          selected.value = []; // Clear the selection after deletion
          // Update month groups
          updateMonthGroups();
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    // Open bulk edit dialog
    const openBulkEditDialog = () => {
      // Reset the form
      bulkEdit.value = {
        updateCategory: false,
        category: '',
        updateScope: false,
        scope: '',
        updateDate: false,
        day: new Date().getDate(),
        month: months.value[new Date().getMonth()],
        year: new Date().getFullYear(),
        updateNotes: false,
        notes: ''
      };
      
      isBulkEditDialogOpen.value = true;
    };

    // Apply bulk edit
    const applyBulkEdit = async () => {
      if (!isBulkEditValid.value || selected.value.length === 0) {
        return;
      }
      
      bulkEditLoading.value = true;
      
      try {
        const selectedIds = selected.value.map(expense => expense.ExpenseID);
        // Create update payload
        const updates = {};
        
        if (bulkEdit.value.updateCategory) {
          updates.category = bulkEdit.value.category;
        }
        
        if (bulkEdit.value.updateScope) {
          updates.scope = bulkEdit.value.scope;
        }
        
        if (bulkEdit.value.updateDate) {
          updates.day = bulkEdit.value.day;
          updates.month = bulkEdit.value.month;
          updates.year = bulkEdit.value.year;
        }
        
        if (bulkEdit.value.updateNotes) {
          updates.notes = bulkEdit.value.notes;
        }
        
        // Make API request to update expenses
        const response = await fetch("/api/bulk_update_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            expenseIds: selectedIds,
            updates: updates
          }),
        });
        
        if (!response.ok) {
          throw new Error("Failed to update expenses");
        }
        
        const data = await response.json();
        if (data.success) {
          // Refresh expenses
          await fetchExpenses();
          isBulkEditDialogOpen.value = false;
          selected.value = []; // Clear selection
        }
      } catch (error) {
        console.error("Error updating expenses:", error);
      } finally {
        bulkEditLoading.value = false;
      }
    };

    // New constants for editing expenses
    const isEditDialogOpen = ref(false);
    const selectedExpense = ref(null);
    const editExpense = (expense) => {
      console.log('Editing expense:', expense);
      selectedExpense.value = expense;
      isEditDialogOpen.value = true;
    };
    const handleUpdateExpenses = () => {
      fetchExpenses();
      isEditDialogOpen.value = false;
      showAddExpense.value = false;
    };

    // Toggle for showing the Add Expense form
    const showAddExpense = ref(false);
    const toggleAddExpense = () => {
      showAddExpense.value = !showAddExpense.value;
    };

    // Helper function to get bank name from Plaid account ID
    const getBankName = (accountId) => {
      if (!accountId || !plaidAccounts.value[accountId]) {
        return 'Unknown Account';
      }
      
      const account = plaidAccounts.value[accountId];
      return account.institution || 'Unknown Bank';
    };

    // Helper function to get detailed bank account information
    const getBankAccountDetails = (accountId) => {
      if (!accountId || !plaidAccounts.value[accountId]) {
        return 'Unknown Account';
      }
      
      const account = plaidAccounts.value[accountId];
      const type = account.type ? account.type.charAt(0).toUpperCase() + account.type.slice(1) : '';
      const subtype = account.subtype ? account.subtype.charAt(0).toUpperCase() + account.subtype.slice(1) : '';
      const mask = account.mask ? `****${account.mask}` : '';
      
      return `${account.name || 'Account'} (${type} ${subtype}) ${mask}`;
    };

    // Helper function to get Plaid category if expense category is missing
    const getPlaidCategory = (expense) => {
      if (expense.PlaidPersonalFinanceCategoryPrimary) {
        return expense.PlaidPersonalFinanceCategoryPrimary.replace(/_/g, ' ');
      }
      
      return expense.PlaidMerchantName || expense.PlaidName || 'Uncategorized';
    };

    // Process expenses to add month information
    const processedExpenses = computed(() => {
      if (!expenses.value || expenses.value.length === 0) {
        return [];
      }
      
      return expenses.value.map((expense) => {
        // Ensure we have a valid date to work with
        let date;
        try {
          date = expense.ExpenseDate ? new Date(expense.ExpenseDate) : new Date();
          
          // Check if date is valid (sometimes dates like "1970-01-01" can be problematic)
          if (isNaN(date.getTime())) {
            // Default to current date if invalid
            date = new Date();
          }
        } catch (e) {
          // Default to current date if error
          date = new Date();
        }
        
        // Get month and year
        const month = months.value[date.getMonth()];
        const year = date.getFullYear();
        
        // Format as "Month Year"
        const monthYear = `${month} ${year}`;
        
        return {
          ...expense,
          ExpenseMonth: monthYear,
        };
      });
    });

    // Update month groups when processed expenses change
    watch(processedExpenses, () => {
      updateMonthGroups();
    });

    onMounted(async () => {
      await Promise.all([
        fetchExpenses(),
        fetchPlaidAccounts(),
        fetchCategories(),
        fetchScopes()
      ]);
    });

    return {
      loading,
      search,
      expenses,
      headers,
      selected,
      monthGroups,
      toggleMonthGroup,
      formatCurrency,
      deleteSelectedExpenses,
      isEditDialogOpen,
      selectedExpense,
      editExpense,
      handleUpdateExpenses,
      formatDate,
      processedExpenses,
      showAddExpense,
      toggleAddExpense,
      deleteExpense,
      // Bulk edit
      isBulkEditDialogOpen,
      bulkEditLoading,
      bulkEdit,
      isBulkEditValid,
      openBulkEditDialog,
      applyBulkEdit,
      categories,
      scopes,
      months,
      // Bank account helpers
      getBankName,
      getBankAccountDetails,
      getPlaidCategory,
    };
  },
};
</script>