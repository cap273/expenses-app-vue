<template>
  <v-container>
          <!-- Chart and Time Period Selection -->
        <div class="chart-container mb-5">
          <!-- Time Period Buttons -->
          <v-btn-toggle v-model="selectedTimePeriod" mandatory>
            <v-btn value="month">Month</v-btn>
            <v-btn value="year">Year</v-btn>
            <v-btn value="lifetime">Lifetime</v-btn>
          </v-btn-toggle>

            <!-- Bar Chart -->
            <div class="chart-wrapper" v-if="chartData && chartData.labels && chartData.labels.length > 0">
              <BarChart :data="chartData" :options="chartOptions" />
            </div>
            <!-- Optional: Display a message when there's no data -->
            <div v-else class="no-data-message">
              <p>No expenses to display for the selected time period.</p>
          </div>

        </div>


      <v-text-field
      v-model="search"
      label="Search"
      class="mb-3"
      ></v-text-field>

      <!-- Loading Screen -->
      <div v-if="loading" class="text-center">
        <v-progress-circular indeterminate></v-progress-circular>
      </div>

      <!-- Action Buttons -->
      <v-btn color="red" @click="deleteSelectedExpenses" 
      v-if="selected.length > 0">
        <v-icon left>mdi-trash-can</v-icon>
        Delete 
      </v-btn> 
      <!--  <v-btn color="blue" @click="editExpense(item)">
        <v-icon left>mdi-pencil</v-icon>
        Edit
      </v-btn>  -->
     

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
        <!-- :group-by="['ExpenseMonth']" -->

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

             <!-- Group Header Slot 
          <template v-slot:group="{ group, items }">
            <tr>
              <td :colspan="headers.length + 1" class="group-header">
                <strong>{{ group }}</strong>
              </td>
            </tr>
          </template>
        -->
      </v-data-table>

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
</template>

<style scoped>
.chart-container {
  margin-bottom: 20px;
}

.chart-wrapper {
  position: relative;
  height: 400px; /* Adjust height as needed */
}

.mb-5 {
  margin-bottom: 3rem;
}
.group-header {
  background-color: #f5f5f5;
  font-size: 1.1em;
}
</style>


<script>
import { ref, onMounted, watch, computed } from 'vue';
import InputExpenses from './InputExpenses.vue';
//adding charts for expenses
import { Bar } from 'vue-chartjs';
import { Chart, registerables } from 'chart.js';

//charts
Chart.register(...registerables);

export default {
  components: {
    InputExpenses,
    BarChart: Bar,
  },
  setup() {
    const loading = ref(true);
    const search = ref("");
    const expenses = ref([]);
    const headers = ref([
      { title: 'Scope', align: 'start', value: 'PersonName', sortable: true },
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
    };

    onMounted(fetchExpenses);

    const formatDate = (dateString) => {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      const date = new Date(dateString);
      return date.toLocaleDateString(undefined, options);
    };

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
          const month = date.toLocaleString('default', { month: 'long', year: 'numeric' });
          return {
            ...expense,
            ExpenseMonth: month,
          };
        });
      });

    //new chart capability
    const selectedTimePeriod = ref('month'); // Default to current month

        const chartOptions = {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
        };

              const chartData = computed(() => {
        // Process expenses based on selectedTimePeriod
        const filteredExpenses = expenses.value.filter(expense => {
          const expenseDate = new Date(expense.ExpenseDate);
          const now = new Date();
          if (selectedTimePeriod.value === 'month') {
            return (
              expenseDate.getFullYear() === now.getFullYear() &&
              expenseDate.getMonth() === now.getMonth()
            );
          } else if (selectedTimePeriod.value === 'year') {
            return expenseDate.getFullYear() === now.getFullYear();
          } else if (selectedTimePeriod.value === 'lifetime') {
            return true; // Include all expenses
          }
          return false;
        });

        // Aggregate expenses by category
        const categoryTotals = {};

        filteredExpenses.forEach(expense => {
        const category = expense.ExpenseCategory || 'Uncategorized';
        let amount = 0;

        if (expense.Amount) {
          const amountString = expense.Amount.toString();
          amount = parseFloat(amountString.replace(/[^0-9.-]+/g, ""));
        }

        if (!categoryTotals[category]) {
          categoryTotals[category] = 0;
        }
        categoryTotals[category] += amount;
      });

        const labels = Object.keys(categoryTotals);
        const data = Object.values(categoryTotals);

        // Ensure that labels and datasets are always arrays
        return {
          labels: labels.length > 0 ? labels : ['No Data'],
          datasets: [
            {
              label: 'Total Expenses',
              data: data.length > 0 ? data : [0],
              backgroundColor: labels.length > 0 ? generateColors(labels.length) : ['#CCCCCC'],
            },
          ],
        };
      });


        // Function to generate colors for the chart
        function generateColors(count) {
          const colors = [];
          for (let i = 0; i < count; i++) {
            // Generate colors using HSL for better visual distinction
            const color = `hsl(${(i * 360) / count}, 70%, 50%)`;
            colors.push(color);
          }
          return colors;
        }


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
      selectedTimePeriod,
      chartData,
      chartOptions,
      formatDate,
      tableOptions,
      updateTableOptions,
      processedExpenses,
    };
  },
};
</script>
