<template>
  <div class="page-background">
    <v-container class="content-container py-4">
      <div class="content-box p-4">

        <h2 class="text-h4 mb-6">Overview</h2>

        <!-- 1. Row of summary cards: 
             (A) Total Cash, (B) Spent This Month, (C) Most Spent Categories, (D) Active Scopes -->
        <v-row class="gy-4">
          <!-- (A) Total Cash Balance -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card hover-elevate">
              <div class="d-flex flex-column align-center justify-center">
                <div class="card-label mb-2">Total Cash Balance</div>
                <div v-if="loadingBalances" class="d-flex align-center my-2">
                  <v-progress-circular indeterminate size="24" />
                </div>
                <div v-else :class="amountClass(totalCash, 'value-text')">
                  {{ formatCurrency(totalCash) }}
                </div>
              </div>
            </v-card>
          </v-col>

          <!-- (B) Spent This Month -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card hover-elevate">
              <div class="d-flex flex-column align-center justify-center">
                <div class="card-label mb-2">Spent This Month</div>
                <div v-if="loading" class="d-flex align-center my-2">
                  <v-progress-circular indeterminate size="24" />
                </div>
                <div v-else :class="amountClass(monthlyTotal, 'value-text')">
                  {{ formatCurrency(monthlyTotal) }}
                </div>
              </div>
            </v-card>
          </v-col>

          <!-- (C) Most Spent Categories (Top 5 for current month) -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card hover-elevate">
              <div class="card-label mb-2 text-center">Most Spent Categories</div>
              <div v-if="loading" class="d-flex align-center justify-center my-4">
                <v-progress-circular indeterminate size="24" />
              </div>
              <div v-else-if="topSpentCategories.length > 0" class="categories-list">
                <div 
                  v-for="(cat, idx) in topSpentCategories.slice(0, 3)" 
                  :key="cat.category + idx"
                  class="category-item"
                >
                  <span class="category-name">{{ cat.category }}</span>
                  <span :class="amountClass(cat.amount, 'category-amount')">
                    {{ formatCurrency(cat.amount) }}
                  </span>
                </div>
              </div>
              <div v-else class="text-center text-subtitle-2 my-4">
                No data available
              </div>
            </v-card>
          </v-col>

          <!-- (D) Active Scopes -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card hover-elevate">
              <div class="d-flex flex-column align-center justify-center">
                <div class="card-label mb-2">Active Scopes</div>
                <div v-if="loading" class="d-flex align-center my-2">
                  <v-progress-circular indeterminate size="24" />
                </div>
                <template v-else>
                  <div class="value-text">{{ activeScopes.length }}</div>
                  <div class="scope-summary">
                    {{ scopesSummary }}
                  </div>
                </template>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 2. Second row: (A) Top 5 Recent Transactions, (B) Month Spend Timeline Chart -->
        <v-row class="mt-6 gy-4">
          <!-- (A) Top 5 Recent Transactions -->
          <v-col cols="12" md="6">
            <v-card class="pa-3 hover-elevate" style="height: 100%;">
              <v-card-title class="p-0">Top 5 Recent Transactions</v-card-title>
              <v-divider class="my-2" />
              <div v-if="loading" class="d-flex align-center justify-center">
                <v-progress-circular indeterminate size="24"/>
              </div>
              <div v-else>
                <v-list lines="one">
                  <v-list-item
                    v-for="(tx, idx) in topFiveTransactions"
                    :key="tx.ExpenseID || idx"
                    class="transaction-item"
                  >
                    <v-list-item-content>
                      <v-list-item-title>
                        {{ tx.ExpenseCategory || 'Uncategorized' }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        {{ formatCurrency(tx.Amount) }} on {{ formatDate(tx.ExpenseDate) }}
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </div>
              <v-card-actions>
                <v-spacer />
                <v-btn variant="text" color="primary" @click="$router.push('/view_expenses')">
                  View All Expenses
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>

          <!-- (B) Month Spend Timeline: This Month vs. Last Month -->
          <v-col cols="12" md="6">
            <v-card class="pa-3 hover-elevate" style="height: 100%;">
              <v-card-title class="p-0">Month Spend Timeline</v-card-title>
              <v-divider class="my-2" />
              <div v-if="loading" class="d-flex align-center justify-center mt-4">
                <v-progress-circular indeterminate size="24"/>
              </div>
              <div v-else class="chart-wrapper">
                <!-- Chart component that re-renders on theme change -->
                <apexchart
                  v-if="chartSeries.length && !chartLoading"
                  :key="themeKey"
                  type="line"
                  height="350"
                  :options="chartOptions"
                  :series="chartSeries"
                />
                <div v-else-if="chartLoading" class="d-flex justify-center align-center h-100">
                  <v-progress-circular indeterminate size="32"/>
                </div>
                <div v-else class="text-subtitle-2 d-flex justify-center align-center h-100">
                  No data available
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 3. Connected Bank Accounts (Plaid) -->
        <v-row class="mt-6">
          <v-col cols="12">
            <PlaidAccountsOverview @accounts-fetched="onAccountsFetched" />
          </v-col>
        </v-row>
      </div>
    </v-container>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import PlaidAccountsOverview from './PlaidComponents/PlaidAccountsOverview.vue'
import VueApexCharts from 'vue3-apexcharts'
import { useTheme } from 'vuetify'

export default {
  name: 'Overview',
  components: {
    PlaidAccountsOverview,
    apexchart: VueApexCharts,
  },
  setup() {
    // Theme access
    const theme = useTheme();
    // Add this timezone adjustment function to your setup() function
    const adjustForTimezone = (dateString) => {
      if (!dateString) return new Date();
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return new Date();
      const timezoneOffset = date.getTimezoneOffset() * 60000;
      return new Date(date.getTime() + timezoneOffset);
    };
    
    // Add a theme key to force chart re-render on theme change
    const themeKey = ref(0);
    const chartLoading = ref(false);
    
    // Watch for theme changes
    watch(() => theme.global.name.value, () => {
      // Trigger chart reload when theme changes
      chartLoading.value = true;
      setTimeout(() => {
        themeKey.value++; // Increment key to force re-render
        chartLoading.value = false;
      }, 100);
    });
    
    // Reactive data
    const loading = ref(true);
    const loadingBalances = ref(true);
    const expenses = ref([]);
    const activeScopes = ref([]);
    const totalCash = ref(0);
    const error = ref(null);

    onMounted(() => {
      fetchAllData();
    });

    const fetchAllData = async () => {
      loading.value = true;
      await Promise.all([fetchExpenses(), fetchScopes()]);
      loading.value = false;
    };

    // 1. Fetch expenses
    const fetchExpenses = async () => {
      try {
        const response = await fetch('/api/get_expenses');
        const data = await response.json();
        if (data.success) {
          expenses.value = data.expenses;
        } else {
          throw new Error(data.error || 'Failed to fetch expenses');
        }
      } catch (err) {
        console.error('Error fetching expenses:', err);
        error.value = err.message;
      }
    };

    // 2. Fetch scopes
    const fetchScopes = async () => {
      try {
        const response = await fetch('/api/get_scopes');
        const data = await response.json();
        if (data.success) {
          activeScopes.value = data.scopes;
        } else {
          throw new Error(data.error || 'Failed to fetch scopes');
        }
      } catch (err) {
        console.error('Error fetching scopes:', err);
        error.value = err.message;
      }
    };

// Update the monthlyTotal computed property
const monthlyTotal = computed(() => {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();
  
  return expenses.value
    .filter(e => {
      const d = adjustForTimezone(e.ExpenseDate);
      return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
    })
    .reduce((acc, e) => {
      const amt = parseFloat(String(e.Amount).replace(/[^0-9.-]+/g, '')) || 0;
      return acc + amt;
    }, 0);
});

// Update the topFiveTransactions computed property
const topFiveTransactions = computed(() => {
  return [...expenses.value]
    .sort((a, b) => adjustForTimezone(b.ExpenseDate) - adjustForTimezone(a.ExpenseDate))
    .slice(0, 5);
});

// Update topSpentCategories computed property
const topSpentCategories = computed(() => {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();
  const catMap = {};
  
  expenses.value.forEach(e => {
    const d = adjustForTimezone(e.ExpenseDate);
    if (d.getMonth() === currentMonth && d.getFullYear() === currentYear) {
      const cat = e.ExpenseCategory || 'Uncategorized';
      const amt = parseFloat(String(e.Amount).replace(/[^0-9.-]+/g, '')) || 0;
      catMap[cat] = (catMap[cat] || 0) + amt;
    }
  });
  
  const catArray = Object.entries(catMap)
    .map(([category, amount]) => ({ category, amount }))
    .sort((a, b) => b.amount - a.amount);
    
  return catArray.slice(0, 5);
});

    // (D) Active scopes summary
    const scopesSummary = computed(() => {
      const personal = activeScopes.value.filter(s => s.type === 'personal').length;
      const household = activeScopes.value.filter(s => s.type === 'household').length;
      return `${personal} Personal, ${household} Household`;
    });

    // Callback from Plaid child
    const onAccountsFetched = (totalBalance) => {
      totalCash.value = totalBalance;
      loadingBalances.value = false;
    };

    // -----------------------------------
    // Month Spend Timeline (Line Chart)
    // -----------------------------------
    
    // Get month names for the chart series
    const getMonthName = (monthOffset = 0) => {
      const date = new Date();
      date.setMonth(date.getMonth() - monthOffset);
      return date.toLocaleString('default', { month: 'long' });
    };
    
    // Days in month helper
    const daysInMonth = (year, month) => {
      return new Date(year, month + 1, 0).getDate();
    };

    // Helper: returns array of length = # of days in that month, each element = daily total
    const getDailyTotals = (year, month) => {
  const numDays = daysInMonth(year, month);
  const dailyTotals = Array(numDays).fill(0);
  
  expenses.value.forEach(e => {
    const d = adjustForTimezone(e.ExpenseDate);
    if (d.getMonth() === month && d.getFullYear() === year) {
      const dayIndex = d.getDate() - 1; // zero-based index
      const amt = parseFloat(String(e.Amount).replace(/[^0-9.-]+/g, "")) || 0;
      dailyTotals[dayIndex] += amt;
    }
  });
  
  return dailyTotals;
};
    // Chart series with actual month names
    const chartSeries = computed(() => {
      if (!expenses.value.length) return [];

      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();

      // Current month data
      const thisMonthDaily = getDailyTotals(currentYear, currentMonth);

      // Previous month data
      let lastMonth = currentMonth - 1;
      let lastMonthYear = currentYear;
      if (lastMonth < 0) {
        lastMonth = 11;
        lastMonthYear -= 1;
      }
      const lastMonthDaily = getDailyTotals(lastMonthYear, lastMonth);

      return [
        {
          name: getMonthName(0), // Current month name
          data: thisMonthDaily,
        },
        {
          name: getMonthName(1), // Previous month name
          data: lastMonthDaily,
        },
      ];
    });

    // Chart options with proper theme integration
    const chartOptions = computed(() => {
      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();
      const maxDays = daysInMonth(currentYear, currentMonth);
      const categories = Array.from({ length: maxDays }, (_, i) => i + 1);
      
      // Get theme colors directly from Vuetify theme
      const isDark = theme.global.current.value.dark;
      
      // Get the actual color values from the theme
      // Use theme tokens for consistent styling
      const currentTheme = theme.global.current.value;
      const textColor = isDark ? '#FFFFFF' : '#000000';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      const backgroundColor = isDark ? '#1E1E1E' : '#FFFFFF';
      
      return {
        chart: {
          id: 'expense-timeline',
          type: 'line',
          fontFamily: 'inherit',
          toolbar: { show: false },
          animations: { enabled: true },
          background: 'transparent',
          foreColor: textColor, // This is key for text colors
        },
        
        // Use brand colors for consistency
        colors: ['#1976d2', '#4caf50'],
        
        // Fix tooltip duplication issue while keeping useful information
        tooltip: { 
          enabled: true,
          theme: isDark ? 'dark' : 'light',
          shared: true, // Use shared tooltip for multiple series
          intersect: false, // Don't require cursor to intersect exactly
          custom: undefined, // Remove custom tooltip, use default with formatting
          x: {
            show: true,
            formatter: (val) => `Day ${val}`
          },
          y: {
            formatter: val => formatCurrency(val),
          },
          marker: {
            show: true,
          },
          style: {
            fontSize: '12px',
            fontFamily: 'inherit'
          }
        },
        
        // Clean, smooth lines with proper styling
        stroke: {
          curve: 'smooth',
          width: 3
        },
        
        // No data labels on the lines
        dataLabels: { 
          enabled: false 
        },
        
        // X-axis styling
        xaxis: {
          categories: categories,
          labels: {
            style: {
              colors: textColor, // Apply color to all labels
              fontFamily: 'inherit',
            }
          },
          axisBorder: {
            show: true,
            color: gridColor
          },
          axisTicks: {
            show: true,
            color: gridColor
          },
          title: {
            text: 'Day of Month',
            style: {
              color: textColor,
              fontFamily: 'inherit',
            }
          }
        },
        
        // Y-axis styling with currency formatter
        yaxis: {
          labels: {
            formatter: (val) => formatCurrency(val),
            style: {
              colors: textColor,
              fontFamily: 'inherit',
            }
          },
          title: {
            style: {
              color: textColor,
              fontFamily: 'inherit',
            }
          }
        },
        
        // Grid lines styling - only horizontal lines for money
        grid: {
          show: true,
          borderColor: gridColor,
          strokeDashArray: 4,
          position: 'back',
          xaxis: {
            lines: {
              show: false // Turn off vertical grid lines
            }
          },
          yaxis: {
            lines: {
              show: true,
              opacity: 0.3
            }
          },
          padding: {
            top: 0,
            right: 0,
            bottom: 0,
            left: 10
          }
        },
        
        // Legend styling
        legend: {
          position: 'top',
          horizontalAlign: 'center',
          labels: {
            colors: textColor
          },
          markers: {
            width: 12,
            height: 12,
            radius: 12
          }
        },
        
        // Data point markers styling
        markers: {
          size: 6,
          strokeWidth: 0,
          hover: {
            size: 8
          }
        }
      };
    });

    // -----------------------------------
    // Formatting helpers
    // -----------------------------------
    const formatCurrency = (val) => {
      if (typeof val === 'string') {
        val = parseFloat(val.replace(/[^0-9.-]+/g, '')) || 0;
      }
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(val);
    };

    const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = adjustForTimezone(dateStr);
  return d.toLocaleDateString();
};

    // Color-coded amounts
    const amountClass = (val, baseClass = 'text-h5') => {
      if (val < 0) return `${baseClass} text-error`;
      if (val > 0) return `${baseClass} text-success`;
      return baseClass;
    };

    return {
      // Data
      loading,
      loadingBalances,
      error,
      expenses,
      activeScopes,
      totalCash,
      themeKey,
      chartLoading,

      // Computed
      monthlyTotal,
      topFiveTransactions,
      topSpentCategories,
      scopesSummary,
      chartSeries,
      chartOptions,

      // Methods
      formatCurrency,
      formatDate,
      amountClass,
      onAccountsFetched,
      adjustForTimezone,
    };
  },
};
</script>

<style scoped>
/* Summary card styling for consistency */
.summary-card {
  height: 150px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-label {
  font-size: 1rem;
  font-weight: 500;
  color: var(--v-theme-on-surface);
  opacity: 0.8;
  text-align: center;
}

.value-text {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
  text-align: center;
}

.scope-summary {
  font-size: 0.875rem;
  color: var(--v-theme-on-surface);
  opacity: 0.7;
  text-align: center;
  margin-top: 4px;
}

/* Categories styling */
.categories-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 8px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.category-name {
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 65%;
}

.category-amount {
  font-size: 0.875rem;
  font-weight: 600;
  text-align: right;
}

/* Card hover effect */
.hover-elevate:hover {
  box-shadow: var(--v-theme-elevation-4);
}

/* Transaction item styling */
.transaction-item {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.transaction-item:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.05);
}

/* Text colors for amounts */
.text-success {
  color: #4caf50 !important;
}

.text-error {
  color: #f44336 !important;
}

/* Chart container */
.chart-wrapper {
  position: relative;
  height: 350px;
  padding: 10px 0;
}

/* Make sure chart size is correct */
:deep(.apexcharts-canvas) {
  margin: 0 auto !important;
}

:deep(.apexcharts-inner) {
  width: 100% !important;
}

/* Chart needs its full height */
.h-100 {
  height: 100%;
}

/* Hide additional tooltips from Apex - remove this since we want to show the tooltips */
</style>