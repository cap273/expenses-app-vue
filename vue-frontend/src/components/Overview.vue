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
            <v-card class="pa-3 hover-elevate">
              <div class="d-flex flex-column align-center">
                <div class="text-subtitle-1 mb-1">Total Cash Balance</div>
                <div v-if="loadingBalances" class="d-flex align-center">
                  <v-progress-circular indeterminate size="20" />
                </div>
                <div v-else :class="amountClass(totalCash)">
                  {{ formatCurrency(totalCash) }}
                </div>
              </div>
            </v-card>
          </v-col>

          <!-- (B) Spent This Month -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-3 hover-elevate">
              <div class="d-flex flex-column align-center">
                <div class="text-subtitle-1 mb-1">Spent This Month</div>
                <div v-if="loading" class="d-flex align-center">
                  <v-progress-circular indeterminate size="20" />
                </div>
                <div v-else :class="amountClass(monthlyTotal)">
                  {{ formatCurrency(monthlyTotal) }}
                </div>
              </div>
            </v-card>
          </v-col>

          <!-- (C) Most Spent Categories (Top 5 for current month) -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-3 hover-elevate" style="height: 100%;">
              <v-card-title class="p-0">Most Spent Categories</v-card-title>
              <v-divider class="my-2" />
              <div v-if="loading" class="d-flex align-center justify-center mt-4">
                <v-progress-circular indeterminate size="24" />
              </div>
              <div v-else>
                <v-list lines="one">
                  <v-list-item
                    v-for="(cat, idx) in topSpentCategories"
                    :key="cat.category + idx"
                  >
                    <v-list-item-content>
                      <v-list-item-title>
                        {{ cat.category }}
                      </v-list-item-title>
                      <v-list-item-subtitle
                        :class="amountClass(cat.amount, 'subtitle-2')"
                      >
                        {{ formatCurrency(cat.amount) }}
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </div>
            </v-card>
          </v-col>

          <!-- (D) Active Scopes -->
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-3 hover-elevate">
              <div class="d-flex flex-column align-center">
                <div class="text-subtitle-1 mb-1">Active Scopes</div>
                <div v-if="loading" class="d-flex align-center">
                  <v-progress-circular indeterminate size="20" />
                </div>
                <template v-else>
                  <div class="text-h5">{{ activeScopes.length }}</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ scopesSummary }}
                  </div>
                </template>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 2. Second row: (A) Top 5 Recent Transactions, (B) Month Spend Timeline Chart -->
        <v-row class="mt-6 gy-4" align="stretch">
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
              <div v-else>
                <!-- Example line chart using apexcharts -->
                <apexchart
                  v-if="chartSeries.length"
                  type="line"
                  height="250"
                  :options="chartOptions"
                  :series="chartSeries"
                />
                <div v-else class="text-subtitle-2">
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
/* If you haven't already, install apexcharts & vue3-apexcharts:
     npm install apexcharts vue3-apexcharts
   Then either import & use it globally, or import locally as shown:
*/
import { ref, onMounted, computed } from 'vue'
import PlaidAccountsOverview from './PlaidComponents/PlaidAccountsOverview.vue'
import VueApexCharts from 'vue3-apexcharts'

export default {
  name: 'Overview',
  components: {
    PlaidAccountsOverview,
    apexchart: VueApexCharts, // local registration of apexchart
  },
  setup() {
    // Reactive data
    const loading = ref(true)
    const loadingBalances = ref(true)
    const expenses = ref([])
    const activeScopes = ref([])
    const totalCash = ref(0)
    const error = ref(null)

    onMounted(() => {
      fetchAllData()
    })

    const fetchAllData = async () => {
      loading.value = true
      await Promise.all([fetchExpenses(), fetchScopes()])
      loading.value = false
    }

    // 1. Fetch expenses
    const fetchExpenses = async () => {
      try {
        const response = await fetch('/api/get_expenses')
        const data = await response.json()
        if (data.success) {
          expenses.value = data.expenses
        } else {
          throw new Error(data.error || 'Failed to fetch expenses')
        }
      } catch (err) {
        console.error('Error fetching expenses:', err)
        error.value = err.message
      }
    }

    // 2. Fetch scopes
    const fetchScopes = async () => {
      try {
        const response = await fetch('/api/get_scopes')
        const data = await response.json()
        if (data.success) {
          activeScopes.value = data.scopes
        } else {
          throw new Error(data.error || 'Failed to fetch scopes')
        }
      } catch (err) {
        console.error('Error fetching scopes:', err)
        error.value = err.message
      }
    }

    // (A) This Month's total
    const monthlyTotal = computed(() => {
      const now = new Date()
      const currentMonth = now.getMonth()
      const currentYear = now.getFullYear()
      const sum = expenses.value
        .filter(e => {
          const d = new Date(e.ExpenseDate)
          return d.getMonth() === currentMonth && d.getFullYear() === currentYear
        })
        .reduce((acc, e) => {
          const amt = parseFloat(String(e.Amount).replace(/[^0-9.-]+/g, '')) || 0
          return acc + amt
        }, 0)
      return sum
    })

    // (B) Top 5 Recent Transactions
    const topFiveTransactions = computed(() => {
      return [...expenses.value]
        .sort((a, b) => new Date(b.ExpenseDate) - new Date(a.ExpenseDate))
        .slice(0, 5)
    })

    // (C) Most Spent Categories (Top 5) for current month
    const topSpentCategories = computed(() => {
      const now = new Date()
      const currentMonth = now.getMonth()
      const currentYear = now.getFullYear()
      const catMap = {}
      expenses.value.forEach(e => {
        const d = new Date(e.ExpenseDate)
        if (d.getMonth() === currentMonth && d.getFullYear() === currentYear) {
          const cat = e.ExpenseCategory || 'Uncategorized'
          const amt = parseFloat(String(e.Amount).replace(/[^0-9.-]+/g, '')) || 0
          catMap[cat] = (catMap[cat] || 0) + amt
        }
      })
      const catArray = Object.entries(catMap).map(([category, amount]) => ({ category, amount }))
      catArray.sort((a, b) => b.amount - a.amount)
      return catArray.slice(0, 5)
    })

    // (D) Active scopes summary
    const scopesSummary = computed(() => {
      const personal = activeScopes.value.filter(s => s.type === 'personal').length
      const household = activeScopes.value.filter(s => s.type === 'household').length
      return `${personal} Personal, ${household} Household`
    })

    // Callback from Plaid child
    const onAccountsFetched = (totalBalance) => {
      totalCash.value = totalBalance
      loadingBalances.value = false
    }

    // -----------------------------------
    // Month Spend Timeline (Line Chart)
    // "This month" vs. "Last month"
    // -----------------------------------
    // 1) build daily totals for each day of the current month
    // 2) build daily totals for each day of the previous month
    // 3) produce an apexcharts series with 2 lines

    const daysInMonth = (year, month) => {
      return new Date(year, month + 1, 0).getDate()
    }

    // Helper: returns array of length = # of days in that month, each element = daily total
    const getDailyTotals = (year, month) => {
      const numDays = daysInMonth(year, month)
      const dailyTotals = Array(numDays).fill(0)
      expenses.value.forEach(e => {
        const d = new Date(e.ExpenseDate)
        if (d.getMonth() === month && d.getFullYear() === year) {
          const dayIndex = d.getDate() - 1 // zero-based index
          const amt = parseFloat(String(e.Amount).replace(/[^0-9.-]+/g, '')) || 0
          dailyTotals[dayIndex] += amt
        }
      })
      // If you want cumulative total each day, you can run a reduce pass:
      // for (let i = 1; i < dailyTotals.length; i++) {
      //   dailyTotals[i] += dailyTotals[i - 1]
      // }
      return dailyTotals
    }

    const chartSeries = computed(() => {
      if (!expenses.value.length) return []

      const now = new Date()
      const currentMonth = now.getMonth()
      const currentYear = now.getFullYear()

      // "This Month"
      const thisMonthDaily = getDailyTotals(currentYear, currentMonth)

      // "Last Month"
      let lastMonth = currentMonth - 1
      let lastMonthYear = currentYear
      if (lastMonth < 0) {
        lastMonth = 11
        lastMonthYear -= 1
      }
      const lastMonthDaily = getDailyTotals(lastMonthYear, lastMonth)

      return [
        {
          name: 'This Month',
          data: thisMonthDaily,
        },
        {
          name: 'Last Month',
          data: lastMonthDaily,
        },
      ]
    })

    // For the X-axis, we just label days [1..maxDays]
    const chartOptions = computed(() => {
      const now = new Date()
      const currentMonth = now.getMonth()
      const currentYear = now.getFullYear()
      const maxDays = daysInMonth(currentYear, currentMonth) // to get typical x-axis length
      const categories = Array.from({ length: maxDays }, (_, i) => i + 1)

      return {
        chart: {
          toolbar: { show: false },
          fontFamily: 'inherit',
        },
        xaxis: {
          categories,
          title: { text: 'Day of Month' },
        },
        yaxis: {
          labels: {
            formatter: val => {
              return formatCurrency(val)
            },
          },
        },
        legend: {
          position: 'top',
        },
        tooltip: {
          y: {
            formatter: val => formatCurrency(val),
          },
        },
      }
    })

    // -----------------------------------
    // Formatting helpers
    // -----------------------------------
    const formatCurrency = (val) => {
      if (typeof val === 'string') {
        val = parseFloat(val.replace(/[^0-9.-]+/g, '')) || 0
      }
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(val)
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }

    // Color-coded amounts
    const amountClass = (val, baseClass = 'text-h5') => {
      if (val < 0) return `${baseClass} text-error`
      if (val > 0) return `${baseClass} text-success`
      return baseClass
    }

    return {
      // Data
      loading,
      loadingBalances,
      error,
      expenses,
      activeScopes,
      totalCash,

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
    }
  },
}
</script>

<style scoped>

.hover-elevate:hover {
  box-shadow: var(--v-theme-elevation-4);
}
.transaction-item {
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.transaction-item:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.05);
}
.text-success {
  color: #4caf50 !important;
}
.text-error {
  color: #f44336 !important;
}

/* Adjust apexchart container if needed */
.apexcharts-canvas {
  /* e.g. dark theme adjustments, font color, etc. */
}
</style>