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
          <v-btn-group v-if="selectedExpenses.length > 0" style="margin-left:20px;">
            <v-btn color="warning" @click="openBulkEditDialog" >
              <v-icon left>mdi-pencil</v-icon>
              ({{ selectedExpenses.length }})
            </v-btn>
            <v-btn color="error" @click="deleteSelectedExpenses">
              <v-icon left>mdi-trash-can</v-icon>
            </v-btn>
          </v-btn-group>
        </div>

        <!-- Debugging help (hidden) -->
        <div v-if="selectedExpenses && selectedExpenses.length > 0" style="display: none;">
          Selected: {{ selectedExpenses.length }} items
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

            <!-- Data Table -->
            <v-data-table
              v-show="group.isOpen"
              :headers="headers"
              :items="group.expenses"
              :search="search"
              :single-select="false" 
              item-key="ExpenseID"
              return-object
              density="compact"
              :items-per-page="-1"
              :no-data-text="'No expenses found'"
              show-select
              v-model="selectedExpenses"
              class="elevation-1 expense-table mb-4"
              :hide-default-header="false"
              hover
            >
              <!-- Source Field (Bank Account) -->
              <template #item.Source="{ item }">
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
              <template #item.ScopeName="{ item }">
                {{ item.ScopeName }}
                <v-chip
                  size="x-small"
                  :color="item.ScopeType === 'personal' ? 'blue' : 'purple'"
                  class="ml-1"
                  variant="flat"
                >
                  {{ item.ScopeType.charAt(0).toUpperCase() }}
                </v-chip>
              </template>

              <!-- Expense Date Column -->
              <template #item.ExpenseDate="{ item }">
                {{ formatDate(adjustForTimezone(item.ExpenseDate)) }}
              </template>

              <!-- Category Column with Icons for Plaid Transactions -->
              <template #item.ExpenseCategory="{ item }">
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
              <template #item.actions="{ item }">
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
            Bulk Edit {{ selectedExpenses.length }} Expenses
          </v-card-title>
          <v-card-text>
            <v-alert type="info" variant="tonal" class="mb-4">
              Choose which fields to update. Only selected fields will be changed.
            </v-alert>
            
            <!-- Edit Fields -->
            <v-row>
              <v-col cols="12" sm="6">
                <v-checkbox
                  v-model="bulkEdit.updateCategory"
                  label="Update Category"
                ></v-checkbox>
                <v-select
                  v-if="bulkEdit.updateCategory"
                  v-model="bulkEdit.category"
                  :items="categories"
                  label="New Category"
                  class="ml-4"
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6">
                <v-checkbox
                  v-model="bulkEdit.updateScope"
                  label="Update Scope"
                ></v-checkbox>
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
                <v-checkbox
                  v-model="bulkEdit.updateDate"
                  label="Update Date"
                ></v-checkbox>
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
                <v-checkbox
                  v-model="bulkEdit.updateNotes"
                  label="Update Notes"
                ></v-checkbox>
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
              Apply to {{ selectedExpenses.length }} Expenses
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
  transition: transform 0.3s ease;
}

/* Rotate icon when the form is toggled open */
.rotate-icon {
  transform: rotate(135deg);
}

/* Circular button styling */
.circle-btn {
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Hover effects for the action buttons */
.v-btn.v-btn--icon {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.v-btn.v-btn--icon:hover {
  opacity: 1;
}

/* Table rows and action buttons */
.expense-table :deep(.v-data-table__tr) {
  transition: background-color 0.2s ease;
}

.expense-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(0, 0, 0, 0.03);
}

.action-buttons {
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
}

.expense-table :deep(.v-data-table__tr:hover) .action-buttons {
  opacity: 1;
}

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
    // Reactive properties
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

    // The array to hold selected rows
    const selectedExpenses = ref([]);

    const plaidAccounts = ref({});
    const categories = ref([]);
    const scopes = ref([]);
    const monthGroups = ref([]);

    // Bulk edit
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

    const months = ref([
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ]);

    const isBulkEditValid = computed(() => {
      if (
        !bulkEdit.value.updateCategory &&
        !bulkEdit.value.updateScope &&
        !bulkEdit.value.updateDate &&
        !bulkEdit.value.updateNotes
      ) {
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

    // Adjust for timezone
    const adjustForTimezone = (dateString) => {
      if (!dateString) return new Date();
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return new Date();
      const timezoneOffset = date.getTimezoneOffset() * 60000;
      return new Date(date.getTime() + timezoneOffset);
    };

    // Processed expenses
    const processedExpenses = computed(() => {
      if (!expenses.value || expenses.value.length === 0) {
        return [];
      }
      return expenses.value.map((expense) => {
        let date;
        let dateStr = expense.ExpenseDate;
        try {
          if (!dateStr || dateStr === "" || dateStr.includes("1970-01-01")) {
            dateStr = expense.CreateDate || new Date().toISOString();
          }
          date = adjustForTimezone(dateStr);
        } catch (e) {
          console.error("Date parsing error:", e);
          date = new Date();
        }
        const month = months.value[date.getMonth()];
        const year = date.getFullYear();
        const monthYear = `${month} ${year}`;
        if (year <= 1980) {
          console.log("Suspicious date detected:", {
            original: expense.ExpenseDate,
            parsed: date.toISOString(),
            expenseId: expense.ExpenseID
          });
        }
        return {
          ...expense,
          ExpenseMonth: monthYear,
          ParsedDate: date
        };
      });
    });

    // Group by month, sort newest first
    const updateMonthGroups = () => {
      const groupedExpenses = {};
      const sortedExpenses = [...processedExpenses.value].sort((a, b) => b.ParsedDate - a.ParsedDate);
      sortedExpenses.forEach((expense) => {
        const month = expense.ExpenseMonth;
        if (!groupedExpenses[month]) {
          groupedExpenses[month] = {
            month,
            expenses: [],
            total: 0,
            isOpen: true
          };
        }
        groupedExpenses[month].expenses.push(expense);
        const amount = parseFloat(expense.Amount?.toString().replace(/[^0-9.-]+/g, "") || 0);
        groupedExpenses[month].total += amount;
      });
      // Sort by year desc, then month desc
      const monthOrder = {
        'January': 0, 'February': 1, 'March': 2, 'April': 3,
        'May': 4, 'June': 5, 'July': 6, 'August': 7,
        'September': 8, 'October': 9, 'November': 10, 'December': 11
      };
      monthGroups.value = Object.values(groupedExpenses).sort((a, b) => {
        const [monthA, yearA] = a.month.split(' ');
        const [monthB, yearB] = b.month.split(' ');
        const yearDiff = parseInt(yearB) - parseInt(yearA);
        if (yearDiff !== 0) return yearDiff;
        return monthOrder[monthB] - monthOrder[monthA];
      });
    };

    // Toggle month group
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

    // API fetches
    const fetchPlaidAccounts = async () => {
      try {
        const response = await fetch('/api/get_plaid_items');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.items) {
            for (const item of data.items) {
              try {
                const accountsResponse = await fetch(`/api/get_item_accounts?item_id=${item.item_id}`);
                if (accountsResponse.ok) {
                  const accountsData = await accountsResponse.json();
                  if (accountsData.success && accountsData.accounts) {
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
          updateMonthGroups();
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        loading.value = false;
      }
    };

    // Single delete
    const deleteExpense = async (expenseId) => {
      try {
        const response = await fetch("/api/delete_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ expenseIds: [expenseId] }),
        });
        if (!response.ok) throw new Error("Failed to delete expense");
        const data = await response.json();
        if (data.success) {
          expenses.value = expenses.value.filter(exp => exp.ExpenseID !== expenseId);
          updateMonthGroups();
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    // Bulk delete
    const deleteSelectedExpenses = async () => {
      if (selectedExpenses.value.length === 0) {
        console.log("No expenses selected");
        return;
      }
      const selectedIds = selectedExpenses.value.map(exp => exp.ExpenseID);
      console.log("Selected Expense IDs:", selectedIds);
      try {
        const response = await fetch("/api/delete_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ expenseIds: selectedIds }),
        });
        if (!response.ok) throw new Error("Failed to delete expenses");
        const data = await response.json();
        if (data.success) {
          await fetchExpenses();
          selectedExpenses.value = [];
          alert(`Successfully deleted ${selectedIds.length} expenses`);
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    // Bulk edit
    const openBulkEditDialog = () => {
      // Reset the bulk edit form
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

    const applyBulkEdit = async () => {
      if (!isBulkEditValid.value || selectedExpenses.value.length === 0) {
        return;
      }
      bulkEditLoading.value = true;
      try {
        const selectedIds = selectedExpenses.value.map(expense => expense.ExpenseID);
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
        const response = await fetch("/api/bulk_update_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            expenseIds: selectedIds,
            updates: updates
          }),
        });
        if (!response.ok) throw new Error("Failed to update expenses");
        const data = await response.json();
        if (data.success) {
          await fetchExpenses();
          isBulkEditDialogOpen.value = false;
          selectedExpenses.value = [];
        }
      } catch (error) {
        console.error("Error updating expenses:", error);
      } finally {
        bulkEditLoading.value = false;
      }
    };

    // Edit expense
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

    // Toggle add expense form
    const showAddExpense = ref(false);
    const toggleAddExpense = () => {
      showAddExpense.value = !showAddExpense.value;
    };

    // Bank account helpers
    const getBankName = (accountId) => {
      if (!accountId || !plaidAccounts.value[accountId]) {
        return 'Unknown Account';
      }
      const account = plaidAccounts.value[accountId];
      return account.institution || 'Unknown Bank';
    };

    const getBankAccountDetails = (accountId) => {
      if (!accountId || !plaidAccounts.value[accountId]) {
        return 'Unknown Account';
      }
      const account = plaidAccounts.value[accountId];
      const type = account.type
        ? account.type.charAt(0).toUpperCase() + account.type.slice(1)
        : '';
      const subtype = account.subtype
        ? account.subtype.charAt(0).toUpperCase() + account.subtype.slice(1)
        : '';
      const mask = account.mask ? `****${account.mask}` : '';
      return `${account.name || 'Account'} (${type} ${subtype}) ${mask}`;
    };

    const getPlaidCategory = (expense) => {
      if (expense.PlaidPersonalFinanceCategoryPrimary) {
        return expense.PlaidPersonalFinanceCategoryPrimary.replace(/_/g, ' ');
      }
      return expense.PlaidMerchantName || expense.PlaidName || 'Uncategorized';
    };

    // Watch selection for debugging
    watch(selectedExpenses, (newVal) => {
      console.log('Selection changed:', newVal?.length || 0, 'items selected');
    }, { deep: true });

    // Whenever processed expenses change, regroup them
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
      // Refs
      loading,
      search,
      expenses,
      headers,
      selectedExpenses,
      monthGroups,
      showAddExpense,
      isEditDialogOpen,
      selectedExpense,
      isBulkEditDialogOpen,
      bulkEditLoading,
      bulkEdit,

      // Methods
      toggleAddExpense,
      handleUpdateExpenses,
      editExpense,
      deleteExpense,
      deleteSelectedExpenses,
      openBulkEditDialog,
      applyBulkEdit,

      // Computed
      isBulkEditValid,
      processedExpenses,

      // Utils
      toggleMonthGroup,
      formatCurrency,
      adjustForTimezone,
      getBankName,
      getBankAccountDetails,
      getPlaidCategory,
      formatDate,

      // Data
      categories,
      scopes,
      months,
    };
  },
};
</script>