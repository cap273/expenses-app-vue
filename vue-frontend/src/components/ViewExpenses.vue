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
            <v-btn color="red" style="margin-left:20px;" @click="deleteSelectedExpenses" 
          v-if="selected.length > 0">
            <v-icon left>mdi-trash-can</v-icon>
            </v-btn> 
          </div>
          
          <!-- Add Expense Form -->
          <div v-if="showAddExpense">
            <input-expenses @update-expenses="handleUpdateExpenses" />
          </div>

          <!-- Loading Screen -->
          <div v-if="loading" class="text-center">
            <v-progress-circular indeterminate></v-progress-circular>
          </div>

          <v-data-table
            :headers="headers"
            :items="processedExpenses"
            :search="search"
            class="elevation-1"
            item-value="ExpenseID"
            density="compact"
            :no-data-text="'No expenses found'"
            items-per-page="25"
            show-select
            v-model="selected"
            :options="tableOptions"
            @update:options="updateTableOptions"
          >
            <template v-slot:item.ScopeName="{ item }">
              {{ item.ScopeName }} ({{ item.ScopeType }})
            </template>
            <!-- Scoped Slot for Expense Date Column -->
            <template v-slot:item.ExpenseDate="{ item }">
              {{ formatDate(item.ExpenseDate) }}
            </template>

            <!-- Scoped Slot for Actions Column -->
            <template v-slot:item.actions="{ item }">
              <v-btn color="blue" @click="editExpense(item)">
                <v-icon left>mdi-pencil</v-icon>
                Edit
              </v-btn>
            </template>
          </v-data-table>
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
    </v-container>
  </div>
</template>

<style scoped>
.search-add-container {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.search-bar {
  flex-grow: 1;
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

</style>


<script>
import { ref, onMounted, watch, computed, defineComponent, h } from 'vue';
import InputExpenses from './InputExpenses.vue';
import ExpenseChart from './ExpenseCharts.vue';
import { formatDate, parseDateInUTC} from '@/utils/dateUtils.js';


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
      { title: 'Scope', align: 'start', value: 'ScopeName', sortable: true,
        // Add a custom format function to show scope type
        format: (value, item) => `${value} (${item.ScopeType})`
      },
      { title: 'Expense Date', value: 'ExpenseDate', sortable: true },
      { title: 'Amount', value: 'Amount' },
      { title: 'Expense Category', value: 'ExpenseCategory', sortable: true },
      { title: 'Additional Notes', value: 'AdditionalNotes', sortable: true },
      { title: 'Actions', value: 'actions', sortable: false },
    ]);

    const selected = ref([]); // This now holds ExpenseID values

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
          console.log('Fetched Expense Dates:', data.expenses.map(e => new Date(e.ExpenseDate)));
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        loading.value = false;
      }
    };

    const deleteSelectedExpenses = async () => {
      if (selected.value.length === 0) {
        console.log("No expenses selected");
        return;
      }

      console.log("Selected Expense IDs:", selected.value); // Log the selected ExpenseIDs

      try {
        const body = JSON.stringify({ expenseIds: selected.value });

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
            expense => !selected.value.includes(expense.ExpenseID)
          );
          selected.value = []; // Clear the selection after deletion
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    // Watch for changes in `selected` to debug selection behavior
    watch(selected, (newVal) => {
      console.log("Updated selected items (via watch):", newVal);
    });

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

    

    onMounted(fetchExpenses);

    const tableOptions = ref({
        sortBy: ['ExpenseDate'],
        sortDesc: [true], // Set to true for descending order (newest first)
        page: 1,
        itemsPerPage: 25,
      });

      const updateTableOptions = (newOptions) => {
        tableOptions.value = newOptions;
      };

      const processedExpenses = computed(() => {
        return expenses.value.map((expense) => {
          const date = new Date(expense.ExpenseDate);
          const month = date.toLocaleString('en-US', {
            month: 'long',
            year: 'numeric',
            timeZone: 'UTC',
          });
          return {
            ...expense,
            ExpenseMonth: month,
          };
        });
      });


    return {
      loading,
      search,
      expenses,
      headers,
      selected,
      deleteSelectedExpenses,
      isEditDialogOpen,
      selectedExpense,
      editExpense,
      handleUpdateExpenses,
      formatDate,
      tableOptions,
      updateTableOptions,
      processedExpenses,
      showAddExpense,
      toggleAddExpense,
    };
  },
};
</script>
