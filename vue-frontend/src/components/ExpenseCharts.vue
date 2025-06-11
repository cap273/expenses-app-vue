<template>
  <div class="chart-container mb-5">
    <!-- Time Period Buttons -->
    <v-btn-toggle v-model="selectedTimePeriod" mandatory>
      <v-btn value="month">Month</v-btn>
      <v-btn value="year">Year</v-btn>
      <v-btn value="lifetime">Lifetime</v-btn>
    </v-btn-toggle>

    <!-- Settings and Filter Icons -->
    <div class="chart-controls">
      <!-- View Mode Menu -->
      <v-menu
        offset-y
        v-model="isViewModeMenuOpen"
        location="bottom end"
        class="mr-2"
      >
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="mr-2"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-subheader>View By</v-list-subheader>
          <v-list-item
            @click="changeViewMode('category')"
            :class="{ 'v-list-item--active': viewMode === 'category' }"
          >
            <template v-slot:prepend>
              <v-icon>mdi-tag</v-icon>
            </template>
            <v-list-item-title>Category</v-list-item-title>
          </v-list-item>
          <v-list-item
            @click="changeViewMode('merchant')"
            :class="{ 'v-list-item--active': viewMode === 'merchant' }"
          >
            <template v-slot:prepend>
              <v-icon>mdi-store</v-icon>
            </template>
            <v-list-item-title>Merchant</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>

      <!-- Filter Menu -->
      <v-menu
        offset-y
        v-model="isFilterMenuOpen"
        location="bottom end"
        class="mr-2"
      >
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="mr-2"
          >
            <v-icon>mdi-filter</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-subheader>Filter by Scope</v-list-subheader>
          <v-list-item
            v-for="scope in availableScopes"
            :key="scope.name + scope.type"
          >
            <v-checkbox
              v-model="selectedScopes"
              :label="`${scope.name} (${scope.type})`"
              :value="scope"
              hide-details
              dense
            ></v-checkbox>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item>
            <v-btn
              block
              @click="clearFilters"
              color="primary"
              variant="text"
            >
              Clear Filters
            </v-btn>
          </v-list-item>
        </v-list>
      </v-menu>

      <!-- Settings Menu -->
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
    <div v-if="!props.expenses" class="no-data-message">
      <p>Loading expenses...</p>
    </div>
    <div v-else-if="hasChartData" :class="['chart-wrapper', { 'sankey-chart': selectedChartType === 'sankey' }]">
      <Transition name="chart-fade" mode="out-in">
        <component
          :key="selectedChartType"
          :is="currentChartComponent"
          :data="chartData"
          :options="chartOptions"
          :height="selectedChartType === 'sankey' ? 500 : undefined"
        />
      </Transition>
    </div>
    <div v-else class="no-data-message">
      <p>No expenses to display for the selected time period and filters.</p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { Bar, Pie } from 'vue-chartjs';
import { Chart as ChartJS, registerables } from 'chart.js';
import { formatDate, parseDateInUTC} from '@/utils/dateUtils.js';
import { getPlaidCategory } from '@/utils/dataUtilities.js';
import { useTheme } from 'vuetify';
import D3SankeyChart from './D3SankeyChart.vue';

ChartJS.register(...registerables);

// Add currency formatter
const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};


//Actual setup
export default {
  name: 'ExpenseChart',
  components: {
    BarChart: Bar,
    PieChart: Pie,
    D3SankeyChart,
  },
  props: {
    expenses: {
      type: Array,
      required: true,
      default: () => [],
    },
  },
  setup(props) {
    const theme = useTheme();
    const selectedTimePeriod = ref('month');
    const isChartMenuOpen = ref(false);
    const isFilterMenuOpen = ref(false);
    const chartTypes = ref([
      { text: 'Bar Chart', value: 'bar' },
      { text: 'Pie Chart', value: 'pie' },
      { text: 'Sankey Diagram', value: 'sankey' },
    ]);
    const selectedChartType = ref('bar');
    const selectedScopes = ref([]);
    const viewMode = ref('category');
    const isViewModeMenuOpen = ref(false);

    const availableScopes = computed(() => {
      if (!props.expenses) return [];
      
      const scopeMap = new Map();
      props.expenses.forEach(expense => {
        if (expense.ScopeName && expense.ScopeType) {
          const key = `${expense.ScopeName}-${expense.ScopeType}`;
          scopeMap.set(key, {
            name: expense.ScopeName,
            type: expense.ScopeType
          });
        }
      });
      return Array.from(scopeMap.values());
    });

    const clearFilters = () => {
      selectedScopes.value = [];
      isFilterMenuOpen.value = false;
    };

    const changeChartType = (type) => {
      selectedChartType.value = type;
      isChartMenuOpen.value = false;
    };

    const changeViewMode = (mode) => {
      viewMode.value = mode;
      isViewModeMenuOpen.value = false;
    };

    const currentChartComponent = computed(() => {
      const typeMap = {
        bar: 'BarChart',
        pie: 'PieChart',
        sankey: 'D3SankeyChart',
      };
      return typeMap[selectedChartType.value] || 'BarChart';
    });

    const filteredExpensesByDate = computed(() => {
        if (!props.expenses) return [];

          return props.expenses.filter((expense) => {
          const expenseDate = parseDateInUTC(expense.ExpenseDate);

          const now = parseDateInUTC(new Date().toISOString());

          if (selectedTimePeriod.value === 'month') {
            return (
              expenseDate.getUTCFullYear() === now.getUTCFullYear() &&
              expenseDate.getUTCMonth() === now.getUTCMonth()
            );
          } else if (selectedTimePeriod.value === 'year') {
            return expenseDate.getUTCFullYear() === now.getUTCFullYear();
          } else {
            return true; // lifetime
          }
        });
      });

    const filteredExpenses = computed(() => {
      if (!filteredExpensesByDate.value) return [];
      
      if (selectedScopes.value.length === 0) {
        return filteredExpensesByDate.value;
      }
      return filteredExpensesByDate.value.filter(expense => 
        selectedScopes.value.some(scope => 
          scope.name === expense.ScopeName && scope.type === expense.ScopeType
        )
      );
    });

    const hasChartData = computed(() => {
      if (!chartData.value) return false;
      
      if (selectedChartType.value === 'sankey') {
        return chartData.value?.datasets?.[0]?.data?.length > 0;
      }
      return chartData.value?.labels?.length > 0;
    });

    const chartOptions = computed(() => {
      const isDark = theme.global.current.value.dark;
      const textColor = isDark ? '#FFFFFF' : '#000000';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

      // Sankey charts are handled by D3SankeyChart component
      if (selectedChartType.value === 'sankey') {
        return {};
      }

      // Base options for all chart types
      const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: selectedChartType.value !== 'bar',
            labels: {
              color: textColor,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            titleColor: textColor,
            bodyColor: textColor,
            backgroundColor: isDark ? '#424242' : '#FFFFFF',
            borderColor: gridColor,
            callbacks: {
              label: function(context) {
                if (selectedChartType.value === 'pie') {
                  const label = context.label || '';
                  const value = formatCurrency(context.raw);
                  return `${label}: ${value}`;
                } else {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  if (context.parsed.y !== null) {
                    label += formatCurrency(context.parsed.y);
                  }
                  return label;
                }
              }
            }
          }
        }
      };

      // Add scales configuration only for bar charts
      if (selectedChartType.value === 'bar') {
        baseOptions.scales = {
          y: {
            beginAtZero: true,
            grid: {
              color: gridColor,
            },
            ticks: {
              color: textColor,
              callback: function(value) {
                return formatCurrency(value);
              }
            }
          },
          x: { 
            grid: {
              color: gridColor,
            },
            ticks: {
              color: textColor,
              callback: function(value) {
                // Truncate long category/merchant names
                const label = this.getLabelForValue(value);
                const maxLength = viewMode.value === 'merchant' ? 25 : 20;
                if (label.length > maxLength) {
                  return label.substr(0, maxLength - 3) + '...';
                }
                return label;
              }
            }
          }
        };
      }

      return baseOptions;
    });

    const chartData = computed(() => {
      if (!filteredExpenses.value) return null;

      const isViewByMerchant = viewMode.value === 'merchant';

      if (selectedChartType.value === 'sankey') {
        // Group expenses by category or merchant and calculate totals
        const totals = {};
        
        filteredExpenses.value.forEach((expense) => {
          let groupKey;
          if (isViewByMerchant) {
            groupKey = expense.PlaidMerchantName || expense.PlaidName || expense.Merchant || 'Unknown Merchant';
          } else {
            groupKey = expense.ExpenseCategory || getPlaidCategory(expense) || 'Uncategorized';
          }
          const amount = parseFloat(expense.Amount?.toString().replace(/[^0-9.-]+/g, "") || 0);
          
          totals[groupKey] = (totals[groupKey] || 0) + amount;
        });

        // Create Sankey flows from "Total Expenses" to each group
        const sankeyData = [];
        
        Object.entries(totals).forEach(([group, amount]) => {
          sankeyData.push({
            from: 'Total Expenses',
            to: group,
            flow: amount,
          });
        });

        return {
          datasets: [{
            data: sankeyData
          }]
        };
      }

      const totals = {};
      filteredExpenses.value.forEach((expense) => {
        let groupKey;
        if (isViewByMerchant) {
          groupKey = expense.PlaidMerchantName || expense.PlaidName || expense.Merchant || 'Unknown Merchant';
        } else {
          groupKey = expense.ExpenseCategory || 'Uncategorized';
        }
        const amount = parseFloat(expense.Amount?.toString().replace(/[^0-9.-]+/g, "") || 0);
        totals[groupKey] = (totals[groupKey] || 0) + amount;
      });

      const labels = Object.keys(totals);
      const data = Object.values(totals);

      return {
        labels: labels.length > 0 ? labels : ['No Data'],
        datasets: [{
          label: isViewByMerchant ? 'Total Expenses by Merchant' : 'Total Expenses by Category',
          data: data.length > 0 ? data : [0],
          backgroundColor: labels.length > 0 ? generateColors(labels.length) : ['#CCCCCC'],
        }],
      };
    });

    function generateColors(count) {
      return Array.from({ length: count }, (_, i) => 
        `hsl(${(i * 360) / count}, 70%, 50%)`
      );
    }


    return {
      props,
      selectedTimePeriod,
      isChartMenuOpen,
      isFilterMenuOpen,
      chartTypes,
      selectedChartType,
      selectedScopes,
      availableScopes,
      viewMode,
      isViewModeMenuOpen,
      changeViewMode,
      clearFilters,
      changeChartType,
      currentChartComponent,
      hasChartData,
      chartOptions,
      chartData,
      formatCurrency,
    };
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  margin-bottom: 20px;
  background-color: var(--v-surface-color);
  color: var(--v-on-surface-color);
}

.chart-controls {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
}

.chart-wrapper {
  position: relative;
  height: 400px;
  margin-top: 40px;
  background-color: var(--v-surface-variant-color);
  border-radius: 8px;
  transition: height 0.5s ease-in-out;
}

.chart-wrapper.sankey-chart {
  height: 700px;
  min-height: 700px;
}

@media (max-width: 768px) {
  .chart-wrapper.sankey-chart {
    height: 600px;
    min-height: 600px;
  }
}


/* Transition Animations */
.chart-fade-enter-active,
.chart-fade-leave-active {
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.chart-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.chart-fade-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

.no-data-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: var(--v-text-secondary-color);
  font-style: italic;
}

</style>