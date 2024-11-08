<template>
  <div class="page-background">
    <v-container class="content-container">
      <div class="content-box">
        <h2 class="text-h4 mb-6">Overview</h2>
        
        <!-- Summary Cards Row -->
        <v-row class="mb-6">
          <v-col cols="12" md="4">
            <v-card>
              <v-card-item>
                <v-card-title>This Month's Spending</v-card-title>
                <div v-if="loading" class="d-flex align-center mt-2">
                  <v-progress-circular indeterminate size="24" width="2" />
                </div>
                <div v-else class="text-h5 mt-2">
                  {{ formatCurrency(monthlyTotal) }}
                </div>
              </v-card-item>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card>
              <v-card-item>
                <v-card-title>Most Spent On</v-card-title>
                <div v-if="loading" class="d-flex align-center mt-2">
                  <v-progress-circular indeterminate size="24" width="2" />
                </div>
                <template v-else>
                  <div class="text-h5 mt-2">{{ topCategory }}</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatCurrency(topCategoryAmount) }}
                  </div>
                </template>
              </v-card-item>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card>
              <v-card-item>
                <v-card-title>Active Scopes</v-card-title>
                <div v-if="loading" class="d-flex align-center mt-2">
                  <v-progress-circular indeterminate size="24" width="2" />
                </div>
                <template v-else>
                  <div class="text-h5 mt-2">{{ activeScopes.length }}</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ scopesSummary }}
                  </div>
                </template>
              </v-card-item>
            </v-card>
          </v-col>
        </v-row>

        <!-- Plaid Accounts Section -->
        <PlaidAccountsOverview />
      </div>
    </v-container>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import PlaidAccountsOverview from './PlaidComponents/PlaidAccountsOverview.vue';

export default {
  name: 'Overview',
  components: {
    PlaidAccountsOverview,
  },
  setup() {
    const loading = ref(true);
    const expenses = ref([]);
    const activeScopes = ref([]);
    const error = ref(null);

    // Helper function to format currency
    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(amount);
    };

    // Computed property for monthly total
    const monthlyTotal = computed(() => {
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth();
      const currentYear = currentDate.getFullYear();

      return expenses.value
        .filter(expense => {
          const expenseDate = new Date(expense.ExpenseDate);
          return expenseDate.getMonth() === currentMonth && 
                 expenseDate.getFullYear() === currentYear;
        })
        .reduce((total, expense) => {
          const amount = typeof expense.Amount === 'string' 
            ? parseFloat(expense.Amount.replace(/[^0-9.-]+/g, ""))
            : expense.Amount;
          return total + amount;
        }, 0);
    });

    // Computed property for top spending category
    const topCategoryData = computed(() => {
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth();
      const currentYear = currentDate.getFullYear();

      const categoryTotals = expenses.value
        .filter(expense => {
          const expenseDate = new Date(expense.ExpenseDate);
          return expenseDate.getMonth() === currentMonth && 
                 expenseDate.getFullYear() === currentYear;
        })
        .reduce((acc, expense) => {
          const category = expense.ExpenseCategory;
          const amount = typeof expense.Amount === 'string' 
            ? parseFloat(expense.Amount.replace(/[^0-9.-]+/g, ""))
            : expense.Amount;
          acc[category] = (acc[category] || 0) + amount;
          return acc;
        }, {});

      const topCategory = Object.entries(categoryTotals)
        .sort(([,a], [,b]) => b - a)[0] || ['None', 0];

      return {
        category: topCategory[0],
        amount: topCategory[1]
      };
    });

    const topCategory = computed(() => topCategoryData.value.category);
    const topCategoryAmount = computed(() => topCategoryData.value.amount);

    // Computed property for scopes summary
    const scopesSummary = computed(() => {
      const personal = activeScopes.value.filter(scope => scope.type === 'personal').length;
      const household = activeScopes.value.filter(scope => scope.type === 'household').length;
      return `${personal} Personal, ${household} Household`;
    });

    // Fetch expenses data
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

    // Fetch scopes data
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

    // Fetch all data
    const fetchData = async () => {
      loading.value = true;
      try {
        await Promise.all([
          fetchExpenses(),
          fetchScopes()
        ]);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchData);

    return {
      loading,
      monthlyTotal,
      topCategory,
      topCategoryAmount,
      activeScopes,
      scopesSummary,
      formatCurrency,
      error
    };
  }
};
</script>

<style scoped>
.text-caption {
  margin-top: 4px;
}

.v-progress-circular {
  margin-left: 8px;
}
</style>