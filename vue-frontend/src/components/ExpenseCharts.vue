<template>
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
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
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
</template>

<script>
    import { ref, computed, defineComponent, h } from 'vue';
    import { Bar, Pie, Chart } from 'vue-chartjs';
    import { Chart as ChartJS, registerables } from 'chart.js';
    import { SankeyController, Flow } from 'chartjs-chart-sankey';
    
    // Register Chart.js components
    ChartJS.register(...registerables);
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
      name: 'ExpenseChart',
      components: {
        BarChart: Bar,
        PieChart: Pie,
        SankeyChart,
      },
      props: {
        expenses: {
          type: Array,
          required: true,
        },
      },
      setup(props) {
        // Chart reactive variables and computed properties
        const selectedTimePeriod = ref('month'); // Default to current month
        const isChartMenuOpen = ref(false);
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
    
        const chartOptions = computed(() => {
          if (selectedChartType.value === 'sankey') {
            return {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function (context) {
                      const label = context.raw.from + ' → ' + context.raw.to;
                      const value = context.raw.flow || 0;
                      return `${label}: ${value}`;
                    },
                  },
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
          const filteredExpenses = props.expenses.filter((expense) => {
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
          selectedTimePeriod,
          isChartMenuOpen,
          chartTypes,
          selectedChartType,
          changeChartType,
          currentChartComponent,
          hasChartData,
          chartOptions,
          chartData,
        };
      },
    };
    </script>

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
    </style>
    