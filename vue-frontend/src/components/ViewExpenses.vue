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

                <!-- Settings Icon and Menu -->
      <div class="chart-settings">
        <v-menu
          offset-y
          v-model="isChartMenuOpen"
          location="bottom end"
        >
          <template v-slot:activator="{props }">
            <v-btn
              icon
              v-bind="props"
              v-on="on"
            >
              <v-icon>mdi-cog</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item
              v-for="type in chartTypes"
              :key="type.value"
              @click="changeChartType(type.value)"
            >
              <v-list-item-title>{{ type.text }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

            <!-- Charts -->
            <div class="chart-wrapper" v-if="hasChartData">
              <!-- Render the chart based on the selectedChartType -->
              <component
                :is="currentChartComponent"
                :data="chartData"
                :options="chartOptions"
              />
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
  position: relative;
  margin-bottom: 20px;
}

.chart-settings {
  position: absolute;
  top: 0;
  right: 0;
}

.chart-wrapper {
  position: relative;
  height: 400px; /* Adjust height as needed */
  margin-top: 40px; /* Add margin to prevent overlap with settings icon */
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
import { ref, onMounted, watch, computed, defineComponent, h } from 'vue';
import InputExpenses from './InputExpenses.vue';
//adding charts for expenses
import { Bar, Pie, Chart } from 'vue-chartjs';
import { Chart as ChartJS, registerables } from 'chart.js';
import { SankeyController, Flow } from 'chartjs-chart-sankey';

//charts
ChartJS.register(...registerables);
// Register Sankey chart components
ChartJS.register(SankeyController, Flow);

// Define SankeyChart component
const SankeyChart = defineComponent({
  name: 'SankeyChart',
  props: {
    data: Object,
    options: Object,
  },
  setup(props) {
    return () =>
      h(Chart, {
        type: 'sankey',
        data: props.data,
        options: props.options,
      });
  },
});

export default {
  components: {
    InputExpenses,
    BarChart: Bar,
    PieChart: Pie,
    SankeyChart,
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
    const isChartMenuOpen = ref(false);
    const hasChartData = computed(() => {
  if (selectedChartType.value === 'sankey') {
    return (
      chartData.value &&
      chartData.value.datasets &&
      chartData.value.datasets[0] &&
      chartData.value.datasets[0].data &&
      chartData.value.datasets[0].data.length > 0
    );
  } else {
    return (
      chartData.value &&
      chartData.value.labels &&
      chartData.value.labels.length > 0
    );
  }
});


        // Chart Type Selection
        const chartTypes = ref([
      { text: 'Bar Chart', value: 'bar' },
      { text: 'Pie Chart', value: 'pie' },
      { text: 'Sankey Diagram', value: 'sankey' },
    ]);

    const selectedChartType = ref('bar'); // Default chart type

    const changeChartType = (type) => {
      selectedChartType.value = type;
      isChartMenuOpen.value = false;
    };

        // Determine which chart component to render
        const currentChartComponent = computed(() => {
      if (selectedChartType.value === 'bar') {
        return 'BarChart';
      } else if (selectedChartType.value === 'pie') {
        return 'PieChart';
      } else if (selectedChartType.value === 'sankey') {
        return 'SankeyChart'; 
      }
      return 'BarChart';
    });

    const chartOptions = computed(() => {
      if (selectedChartType.value === 'sankey') {
        return {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.dataset.label || '';
                  const value = context.raw.weight || 0;
                  return `${label}: ${value}`;
                },
              },
            },
          },
          scales: {
            x: {
              stacked: true,
            },
            y: {
              stacked: true,
            },
          },
        };
      }
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: selectedChartType.value !== 'bar',
          },
        },
      };
    });

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

        if (selectedChartType.value === 'sankey') {
        // Prepare data for Sankey Diagram
        const sankeyData = [];
        filteredExpenses.forEach((expense) => {
          const source = expense.PersonName || 'Unknown';
          const target = expense.ExpenseCategory || 'Uncategorized';
          let amount = 0;
            if (expense.Amount) {
              const amountString = expense.Amount.toString();
              // Remove any non-numeric characters except for decimal points and minus signs
              amount = parseFloat(amountString.replace(/[^0-9.-]+/g, ""));
            }

          sankeyData.push({
            from: source,
            to: target,
            flow: amount,
          });
        });

        return {
          datasets: [
            {
              label: 'Expense Flows',
              data: sankeyData,
              colorFrom: 'blue',
              colorTo: 'green',
              colorMode: 'gradient',
            },
          ],
        };
      } else {
        // Aggregate expenses by category
        const categoryTotals = {};

        filteredExpenses.forEach((expense) => {
          const category = expense.ExpenseCategory || 'Uncategorized';
          let amount = 0;
          if (expense.Amount) {
            const amountString = expense.Amount.toString();
            // Remove any non-numeric characters except for decimal points and minus signs
            amount = parseFloat(amountString.replace(/[^0-9.-]+/g, ""));
          }

          if (!categoryTotals[category]) {
            categoryTotals[category] = 0;
          }
          categoryTotals[category] += amount;
        });

        const labels = Object.keys(categoryTotals);
        const data = Object.values(categoryTotals);

        return {
          labels: labels.length > 0 ? labels : ['No Data'],
          datasets: [
            {
              label: 'Total Expenses',
              data: data.length > 0 ? data : [0],
              backgroundColor:
                labels.length > 0
                  ? generateColors(labels.length)
                  : ['#CCCCCC'],
            },
          ],
        };
      }
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
      isChartMenuOpen,
      chartTypes,
      selectedChartType,
      changeChartType,
      currentChartComponent,
      hasChartData,
    };
  },
};
</script>
