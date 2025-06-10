<template>
  <div class="page-background">
    <v-container class="content-container py-4">
      <div class="content-box p-4">
        <h2 class="text-h4 mb-6">Overview</h2>

        <!-- 1. Consolidated summary info panel -->
        <v-card class="info-panel mb-6 hover-elevate">
          <v-row class="pa-4 ma-0">
            <!-- Cash Balance with Bank Account Details -->
            <v-col cols="12" md="4" class="info-section">
              <div class="info-title">Total Cash Balance</div>
              <div v-if="loadingBalances" class="d-flex align-center">
                <v-progress-circular indeterminate size="20" width="2" />
              </div>
              <div v-else class="d-flex flex-column align-center">
                <div :class="amountClass(totalCash, 'info-value')">
                  {{ formatCurrency(totalCash) }}
                </div>
                <!-- Bank Account Breakdown -->
                <div class="bank-accounts-container mt-2">
                  <div v-for="(account, index) in bankAccounts" 
                       :key="index" 
                       class="bank-account-item">
                    <v-icon size="small" color="primary" class="mr-1">mdi-bank</v-icon>
                    <span class="bank-name" :title="account.name">{{ account.name }}</span>
                    <span class="bank-balance">{{ formatCurrency(account.balance) }}</span>
                  </div>
                  <div v-if="bankAccounts.length === 0" class="text-caption text-center mt-2">
                    <v-btn size="x-small" color="primary" variant="text" @click="$router.push('/plaid')">
                      <v-icon size="small">mdi-plus</v-icon>
                      Connect a bank
                    </v-btn>
                  </div>
                </div>
              </div>
            </v-col>
            
            <!-- Monthly Spend -->
            <v-col cols="12" md="4" class="info-section">
              <div class="info-title">This Month's Spending</div>
              <div v-if="loading" class="d-flex align-center">
                <v-progress-circular indeterminate size="20" width="2" />
              </div>
              <div v-else class="d-flex flex-column align-center">
                <div :class="amountClass(monthlyTotal, 'info-value')">
                  {{ formatCurrency(monthlyTotal) }}
                </div>
              </div>
            </v-col>

            <!-- Filter by Scope -->
            <v-col cols="12" md="4" class="info-section">
              <div class="d-flex align-items-center justify-center">
                <div class="info-title">Filter by scope:</div>
                <v-btn 
                  icon 
                  variant="text" 
                  color="primary" 
                  @click="$router.push('/household')"
                  size="x-small"
                  class="ml-2"
                >
                  <v-icon size="small">mdi-cog</v-icon>
                </v-btn>
              </div>
              <div v-if="loading" class="d-flex align-center">
                <v-progress-circular indeterminate size="20" width="2" />
              </div>
              <div v-else class="scope-selector-container">
                <v-chip-group
                  v-model="selectedScopes"
                  column
                  multiple
                  class="scope-filters"
                >
                  <v-chip
                    v-for="scope in activeScopes"
                    :key="scope.id"
                    :value="scope.id"
                    filter
                    size="small"
                    variant="elevated"
                    :color="scope.type === 'personal' ? 'blue' : 'purple'"
                  >
                    {{ scope.name }}
                  </v-chip>
                </v-chip-group>
                <div class="text-center mt-1">
                  <v-btn
                    variant="text"
                    size="x-small"
                    @click="selectedScopes = activeScopes.map(s => s.id)"
                    color="primary"
                  >
                    SELECT ALL
                  </v-btn>
                  <v-btn
                    variant="text"
                    size="x-small"
                    @click="selectedScopes = []"
                    color="error"
                    class="ml-2"
                  >
                    CLEAR ALL
                  </v-btn>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card>

        <!-- 2. Second row: Spending Insights, Top Categories -->
        <v-row class="gy-4">
          <!-- (A) Spending Insights -->
          <v-col cols="12" md="4">
            <v-card class="pa-3 hover-elevate h-100">
              <div class="d-flex align-center justify-space-between mb-2">
                <h3 class="text-h6 mb-0">Spending Insights</h3>
              </div>
              <v-divider class="mb-3"></v-divider>
              
              <div v-if="loading" class="d-flex justify-center my-2">
                <v-progress-circular indeterminate size="24" />
              </div>
              <div v-else class="insights-container">
                <div class="donut-container">
                  <apexchart
                    v-if="topSpentCategories.length > 0"
                    type="donut"
                    height="200"
                    :options="categoryChartOptions"
                    :series="categoryChartSeries"
                  />
                  <div v-else class="text-center pt-10">
                    <span class="text-subtitle-2">No spending data available</span>
                  </div>
                </div>
                
                <div class="insights-summary mt-3">
                  <div class="d-flex align-center mb-2">
                    <v-icon color="primary" size="small" class="mr-2">mdi-wallet</v-icon>
                    <span class="text-subtitle-2">Active Scopes: {{ activeScopes.length }}</span>
                  </div>
                  <div class="d-flex align-center mb-2">
                    <v-icon color="primary" size="small" class="mr-2">mdi-calendar</v-icon>
                    <span class="text-subtitle-2">Tracked Since: {{ trackingSince }}</span>
                  </div>
                  <div class="d-flex align-center">
                    <v-icon color="primary" size="small" class="mr-2">mdi-tag-multiple</v-icon>
                    <span class="text-subtitle-2">Top Category: {{ topCategory }}</span>
                  </div>
                </div>
              </div>
            </v-card>
          </v-col>

          <!-- (B) Top Categories -->
          <v-col cols="12" md="8">
            <v-card class="pa-3 hover-elevate h-100">
              <div class="d-flex align-center justify-space-between mb-2">
                <h3 class="text-h6 mb-0">Top Categories</h3>
                <v-menu location="bottom end">
                  <template v-slot:activator="{ props }">
                    <v-btn icon variant="text" v-bind="props" size="small">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item @click="$router.push('/input_expenses')">
                      <v-list-item-title>Add New Expense</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="$router.push('/view_expenses')">
                      <v-list-item-title>View All Expenses</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </div>
              <v-divider class="mb-3"></v-divider>
              
              <div v-if="loading" class="d-flex justify-center my-4">
                <v-progress-circular indeterminate size="24" />
              </div>
              <v-row v-else-if="topSpentCategories.length > 0" class="pa-2">
                <v-col cols="12">
                  <!-- Category list with full category names -->
                  <div class="categories-list">
                    <div 
                      v-for="(cat, idx) in topSpentCategories" 
                      :key="cat.category + idx"
                      class="category-item"
                    >
                      <div class="d-flex align-center category-name-container">
                        <div class="category-bar" 
                          :style="{
                            width: `${getCategoryBarWidth(cat.amount, idx)}%`,
                            backgroundColor: getCategoryColor(idx)
                          }"
                        ></div>
                        <div class="category-name-wrapper ml-2">
                          {{ cat.category }}
                        </div>
                      </div>
                      <span :class="amountClass(cat.amount, 'category-amount')">
                        {{ formatCurrency(cat.amount) }}
                      </span>
                    </div>
                  </div>
                </v-col>
              </v-row>
              <div v-else class="text-center text-subtitle-2 my-4">
                No data available
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 3. Third row: Recent Transactions and Month Spend Timeline -->
        <v-row class="mt-6 gy-4">
          <!-- (A) Recent Transactions as a simple table -->
          <v-col cols="12" md="6">
            <v-card class="pa-3 hover-elevate" style="height: 100%;">
              <div class="d-flex align-center justify-space-between mb-2">
                <h3 class="text-h6 mb-0">Recent Transactions</h3>
                <v-btn 
                  variant="text" 
                  color="primary" 
                  size="small"
                  @click="$router.push('/view_expenses')"
                >
                  View All
                </v-btn>
              </div>
              <v-divider class="mb-3"></v-divider>
              
              <div v-if="loading" class="d-flex align-center justify-center my-4">
                <v-progress-circular indeterminate size="24"/>
              </div>
              <div v-else-if="topFiveTransactions.length > 0" class="recent-transactions">
                <v-table dense>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Merchant/Category</th>
                      <th class="text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(tx, idx) in topFiveTransactions"
                      :key="tx.ExpenseID || idx"
                      class="transaction-row"
                    >
                      <td>{{ formatShortDate(tx.ExpenseDate) }}</td>
                      <td>{{ tx.PlaidMerchantName || tx.ExpenseCategory || 'Uncategorized' }}</td>
                      <td class="text-right" :class="amountClass(parseFloat(tx.Amount.replace(/[^0-9.-]+/g, '')), 'text-body-2')">
                        {{ formatCurrency(parseFloat(tx.Amount.replace(/[^0-9.-]+/g, ''))) }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </div>
              <div v-else class="text-center my-4">
                <p class="text-medium-emphasis">No recent transactions</p>
              </div>
            </v-card>
          </v-col>

          <!-- (B) Month Spend Timeline: Cumulative Chart -->
          <v-col cols="12" md="6">
            <v-card class="pa-3 hover-elevate" style="height: 100%;">
              <div class="d-flex align-center justify-space-between mb-2">
                <h3 class="text-h6 mb-0">Monthly Spending</h3>
                <v-select
                  v-model="timelineView"
                  :items="['Daily', 'Cumulative']"
                  density="compact"
                  hide-details
                  class="timeline-selector"
                  style="max-width: 150px"
                ></v-select>
              </div>
              <v-divider class="mb-3"></v-divider>
              
              <div v-if="loading" class="d-flex align-center justify-center my-4">
                <v-progress-circular indeterminate size="24"/>
              </div>
              <div v-else class="chart-wrapper">
                <!-- Chart component that re-renders on theme change -->
                <apexchart
                  v-if="spendingSeries.length && !chartLoading"
                  :key="themeKey"
                  type="area"
                  height="300"
                  :options="spendingChartOptions"
                  :series="spendingSeries"
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

        <!-- 4. Connected Bank Accounts (Plaid) -->
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
import { formatDate, formatShortDate, adjustForTimezone, daysInMonth, getMonthName } from '@/utils/dateUtils';
import { formatCurrency, amountClass, parseNumericValue } from '@/utils/formatUtils';

export default {
  name: 'Overview',
  components: {
    PlaidAccountsOverview,
    apexchart: VueApexCharts,
  },
  setup() {
    // Theme changes
    const theme = useTheme();
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
    const selectedScopes = ref([]);
    const totalCash = ref(0);
    const error = ref(null);
    const timelineView = ref('Cumulative');
    const bankAccounts = ref([]);
    const trackingSince = ref('N/A');

    onMounted(() => {
      fetchAllData();
      
      // Set tracking since from computed value after data is loaded
      watch(getTrackingSince, (newVal) => {
        trackingSince.value = newVal;
      });
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
          // Select all scopes by default
          selectedScopes.value = data.scopes.map(scope => scope.id);
        } else {
          throw new Error(data.error || 'Failed to fetch scopes');
        }
      } catch (err) {
        console.error('Error fetching scopes:', err);
        error.value = err.message;
      }
    };

    // Filtered expenses based on selected scopes
    const filteredExpenses = computed(() => {
      if (!expenses.value || !selectedScopes.value.length) return [];
      
      return expenses.value.filter(expense => 
        selectedScopes.value.includes(expense.ScopeID)
      );
    });

    // Monthly total computed property
    const monthlyTotal = computed(() => {
      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();
      
      return filteredExpenses.value
        .filter(e => {
          const d = adjustForTimezone(e.ExpenseDate);
          return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
        })
        .reduce((acc, e) => {
          const amt = parseNumericValue(e.Amount);
          return acc + amt;
        }, 0);
    });

    // Top 5 recent transactions
    const topFiveTransactions = computed(() => {
      return [...filteredExpenses.value]
        .sort((a, b) => adjustForTimezone(b.ExpenseDate) - adjustForTimezone(a.ExpenseDate))
        .slice(0, 5);
    });

    // Top spent categories
    const topSpentCategories = computed(() => {
      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();
      const catMap = {};
      
      filteredExpenses.value.forEach(e => {
        const d = adjustForTimezone(e.ExpenseDate);
        if (d.getMonth() === currentMonth && d.getFullYear() === currentYear) {
          const cat = e.ExpenseCategory || 'Uncategorized';
          const amt = parseNumericValue(e.Amount);
          catMap[cat] = (catMap[cat] || 0) + amt;
        }
      });
      
      const catArray = Object.entries(catMap)
        .map(([category, amount]) => ({ category, amount }))
        .sort((a, b) => b.amount - a.amount);
        
      return catArray.slice(0, 5);
    });

    // Active scopes summary
    const scopesSummary = computed(() => {
      const personal = activeScopes.value.filter(s => s.type === 'personal').length;
      const household = activeScopes.value.filter(s => s.type === 'household').length;
      return `${personal} Personal, ${household} Household`;
    });
    
    // Get the top spending category
    const topCategory = computed(() => {
      if (topSpentCategories.value.length > 0) {
        return topSpentCategories.value[0].category;
      }
      return 'None';
    });
    
    // Get tracking since date - earliest expense date
    const getTrackingSince = computed(() => {
      if (expenses.value.length === 0) return 'N/A';
      
      try {
        // Find earliest expense date
        const dates = expenses.value
          .map(e => adjustForTimezone(e.ExpenseDate))
          .filter(d => d instanceof Date && !isNaN(d));
          
        if (dates.length === 0) return 'N/A';
        
        const earliestDate = new Date(Math.min(...dates.map(d => d.getTime())));
        return formatDate(earliestDate);
      } catch (e) {
        console.error('Error calculating tracking since date:', e);
        return 'N/A';
      }
    });

    // Callback from Plaid child
    const onAccountsFetched = (totalBalance) => {
      totalCash.value = totalBalance;
      loadingBalances.value = false;
      
      // Fetch bank accounts info
      fetchBankAccounts();
    };
    
    // Fetch bank account details
    const fetchBankAccounts = async () => {
      try {
        const response = await fetch('/api/get_plaid_items');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.items) {
            const accounts = [];
            
            for (const item of data.items) {
              try {
                const accountsResponse = await fetch(`/api/get_item_accounts?item_id=${item.item_id}`);
                if (accountsResponse.ok) {
                  const accountsData = await accountsResponse.json();
                  if (accountsData.success && accountsData.accounts) {
                    accountsData.accounts.forEach(account => {
                      accounts.push({
                        name: `${item.institution_name} - ${account.name}`,
                        balance: account.balances.available || account.balances.current || 0,
                        type: account.type,
                        subtype: account.subtype
                      });
                    });
                  }
                }
              } catch (e) {
                console.error(`Error fetching accounts for item ${item.item_id}:`, e);
              }
            }
            
            bankAccounts.value = accounts;
          }
        }
      } catch (e) {
        console.error('Error fetching bank accounts:', e);
      }
    };

    // Category Chart Options
          const categoryChartOptions = computed(() => {
      const isDark = theme.global.current.value.dark;
      const textColor = isDark ? '#FFFFFF' : '#000000';
      
      return {
        chart: {
          fontFamily: 'inherit',
          foreColor: textColor,
          toolbar: { show: false },
        },
        labels: topSpentCategories.value.map(c => {
          // Truncate long category names only in chart labels, but keep tooltip with full name
          return c.category.length > 15 ? c.category.slice(0, 12) + '...' : c.category;
        }),
        dataLabels: {
          enabled: false
        },
        plotOptions: {
          pie: {
            donut: {
              size: '70%',
              labels: {
                show: true,
                name: { show: false },
                value: { 
                  show: true,
                  formatter: val => formatCurrency(val)
                },
                total: { 
                  show: true,
                  formatter: w => formatCurrency(
                    w.globals.seriesTotals.reduce((a, b) => a + b, 0)
                  )
                }
              }
            }
          }
        },
        legend: {
          show: false
        },
        tooltip: {
          theme: isDark ? 'dark' : 'light',
          y: {
            formatter: val => formatCurrency(val)
          },
          custom: function({ series, seriesIndex, dataPointIndex, w }) {
            // Show full category name in tooltip
            const category = topSpentCategories.value[seriesIndex].category;
            const value = formatCurrency(series[seriesIndex]);
            return `<div class="apexcharts-tooltip-title" style="font-family: inherit; font-size: 12px;">
                      ${category}
                    </div>
                    <div class="apexcharts-tooltip-series-group">
                      <span class="apexcharts-tooltip-text" style="font-family: inherit; font-size: 12px;">
                        ${value}
                      </span>
                    </div>`;
          }
        },
        colors: getCategoryColors(topSpentCategories.value.length)
      };
    });

    const categoryChartSeries = computed(() => {
      return topSpentCategories.value.map(cat => cat.amount);
    });

    // Get color for category based on index
    const getCategoryColor = (index) => {
      const colors = [
        '#1976d2', '#4caf50', '#ff9800', '#9c27b0', '#f44336',
        '#2196f3', '#8bc34a', '#ffc107', '#673ab7', '#e91e63'
      ];
      return colors[index % colors.length];
    };

    // Calculate category bar width with true proportional scaling
    const getCategoryBarWidth = (amount, index) => {
      if (topSpentCategories.value.length === 0) return 5;
      
      const maxAmount = topSpentCategories.value[0].amount;
      
      // If all amounts are the same, use equal widths
      if (maxAmount === 0) {
        return 70;
      }
      
      // True proportional scaling: each bar is exactly proportional to its value
      // Scale the largest value to 75% to leave room for text, all others are proportional
      const maxWidth = 75;
      const proportionalWidth = (amount / maxAmount) * maxWidth;
      
      // Only apply a very small minimum (2%) for tiny values to remain visible
      const minWidth = 2;
      
      return Math.max(minWidth, Math.round(proportionalWidth));
    };

    // Get an array of colors for categories
    const getCategoryColors = (count) => {
      return Array.from({ length: count }, (_, i) => getCategoryColor(i));
    };

    // Monthly spending timeline data
    const getDailySpending = (year, month) => {
      const numDays = daysInMonth(year, month);
      const dailyTotals = Array(numDays).fill(0);
      
      filteredExpenses.value.forEach(e => {
        const d = adjustForTimezone(e.ExpenseDate);
        if (d.getMonth() === month && d.getFullYear() === year) {
          const dayIndex = d.getDate() - 1; // zero-based index
          const amt = parseNumericValue(e.Amount);
          dailyTotals[dayIndex] += amt;
        }
      });
      
      return dailyTotals;
    };

    // Convert daily totals to cumulative totals
    const getCumulativeTotals = (dailyTotals) => {
      let runningTotal = 0;
      return dailyTotals.map(daily => {
        runningTotal += daily;
        return runningTotal;
      });
    };

    // Spending series based on selected view
    const spendingSeries = computed(() => {
      if (!filteredExpenses.value.length) return [];

      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();

      // Get daily spending for the current month
      const dailyTotals = getDailySpending(currentYear, currentMonth);
      
      // Transform based on selected view
      const data = timelineView.value === 'Cumulative' 
        ? getCumulativeTotals(dailyTotals)
        : dailyTotals;
      
      return [{
        name: timelineView.value === 'Cumulative' ? 'Total Spent' : 'Daily Spending',
        data
      }];
    });

    // Spending chart options
    const spendingChartOptions = computed(() => {
      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();
      const numDays = daysInMonth(currentYear, currentMonth);
      const categories = Array.from({ length: numDays }, (_, i) => i + 1);
      
      // Get theme colors directly from Vuetify theme
      const isDark = theme.global.current.value.dark;
      const textColor = isDark ? '#FFFFFF' : '#000000';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      
      return {
        chart: {
          id: 'spending-timeline',
          type: 'area',
          fontFamily: 'inherit',
          toolbar: { show: false },
          animations: { enabled: true },
          background: 'transparent',
          foreColor: textColor,
        },
        colors: ['#4CAF50'],
        stroke: {
          curve: 'smooth',
          width: 3
        },
        fill: {
          type: 'gradient',
          gradient: {
            shade: isDark ? 'dark' : 'light',
            type: "vertical",
            opacityFrom: 0.7,
            opacityTo: 0.2,
          }
        },
        dataLabels: { 
          enabled: false 
        },
        tooltip: { 
          enabled: true,
          theme: isDark ? 'dark' : 'light',
          y: {
            formatter: val => formatCurrency(val),
          },
          x: {
            formatter: val => `Day ${val}`
          }
        },
        xaxis: {
          categories,
          title: {
            text: 'Day of Month',
            style: {
              color: textColor,
              fontFamily: 'inherit',
            }
          },
          labels: {
            style: {
              colors: textColor,
              fontFamily: 'inherit',
            },
            formatter: (val) => {
              // Only show some day labels to avoid crowding
              return parseInt(val) % 5 === 0 ? val : '';
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
        },
        yaxis: {
          labels: {
            formatter: (val) => formatCurrency(val),
            style: {
              colors: textColor,
              fontFamily: 'inherit',
            }
          }
        },
        grid: {
          show: true,
          borderColor: gridColor,
          strokeDashArray: 4,
          position: 'back',
          xaxis: {
            lines: {
              show: false
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
            right: 10,
            bottom: 0,
            left: 10
          }
        },
      };
    });

    return {
      // Data
      loading,
      loadingBalances,
      error,
      expenses,
      activeScopes,
      selectedScopes,
      totalCash,
      themeKey,
      chartLoading,
      timelineView,
      bankAccounts,
      trackingSince,

      // Computed
      filteredExpenses,
      monthlyTotal,
      topFiveTransactions,
      topSpentCategories,
      scopesSummary,
      spendingSeries,
      spendingChartOptions,
      categoryChartOptions,
      categoryChartSeries,
      topCategory,
      getTrackingSince,

      // Methods
      formatCurrency,
      formatDate,
      formatShortDate,
      amountClass,
      onAccountsFetched,
      adjustForTimezone,
      getCategoryColor,
      getCategoryBarWidth,
      parseNumericValue,
    };
  },
};
</script>

<style scoped>
/* Info Panel Styling */
.info-panel {
  border-radius: 8px;
}

.info-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 20px 16px;
  position: relative;
  min-height: 160px;
}

.info-section:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 25%;
  height: 50%;
  width: 1px;
  background-color: rgba(var(--v-theme-on-surface), 0.1);
}

.info-title {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0.8;
  margin-bottom: 8px;
}

.info-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
}

.info-detail {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.scope-selector-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 4px;
}

/* Bank accounts styling */
.bank-accounts-container {
  width: 100%;
  max-width: 320px;
  max-height: 140px;
  overflow-y: auto;
  padding: 4px;
  margin-top: 8px;
}

.bank-accounts-container::-webkit-scrollbar {
  width: 6px;
}

.bank-accounts-container::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 3px;
}

.bank-accounts-container::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.5);
  border-radius: 3px;
}

.bank-accounts-container::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.7);
}

.bank-account-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 10px 12px;
  background-color: rgba(var(--v-theme-surface-variant), 0.3);
  height: 44px;
  overflow: hidden;
  position: relative;
}

.bank-account-item:hover {
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
}

.bank-name {
  flex: 1;
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.bank-account-item:hover .bank-name {
  overflow: visible;
  white-space: normal;
  word-break: break-word;
  background-color: inherit;
  padding: 2px 4px;
  border-radius: 2px;
}

.bank-balance {
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

/* Insights container */
.insights-container {
  display: flex;
  flex-direction: column;
}

.donut-container {
  height: 200px;
}

.insights-summary {
  padding: 8px;
}

/* Scope filters */
.scope-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Categories styling */
.categories-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.category-name-container {
  flex: 1;
  min-width: 0;
  margin-right: 12px;
}

.category-name-wrapper {
  font-size: 0.875rem;
  min-width: 0;
  white-space: nowrap;
  line-height: 1.3;
  flex: 1;
}

.category-bar {
  height: 16px;
  min-width: 10px;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.category-amount {
  font-size: 0.875rem;
  font-weight: 500;
  text-align: right;
  white-space: nowrap;
}

/* Chart styling */
.chart-container {
  height: 200px;
  position: relative;
}

.chart-wrapper {
  position: relative;
  height: 300px;
}

/* Recent transactions styling */
.transaction-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.transaction-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.05);
}

/* Layout spacing */
.hover-elevate {
  transition: box-shadow 0.3s ease;
}

.hover-elevate:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Timeline selector */
.timeline-selector {
  max-width: 140px;
}

/* Utility classes */
.gap-1 {
  gap: 4px;
}

/* Responsive adjustments */
@media (max-width: 959px) {
  .info-section:not(:last-child)::after {
    display: none;
  }
  
  .info-section {
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  }
  
  .info-section:last-child {
    border-bottom: none;
  }
}
</style>