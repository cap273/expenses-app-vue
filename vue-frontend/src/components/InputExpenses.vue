<template>
  <div class="expense-input-container">
    <v-container class="pa-0">
      <!-- Response Message -->
      <v-alert
        v-if="responseMessage.message"
        :type="responseMessage.type"
        class="mb-6"
        dismissible
        @click:close="responseMessage.message = ''"
      >
        {{ responseMessage.message }}
      </v-alert>

      <v-form ref="form" @submit.prevent="submitExpenses">
          <!-- Expense Cards -->
          <div v-for="(expense, index) in expenses" :key="`expense-${index}-${expense.rowKey}`" class="expense-card-container">
            <v-card class="expense-card hover-elevate mb-4" elevation="2">
              <v-card-title class="pb-2">
                <div class="d-flex justify-space-between align-center w-100">
                  <span class="expense-title">
                    {{ expenses.length > 1 ? `Expense ${index + 1}` : 'Expense Details' }}
                  </span>
                  <div v-if="expenses.length > 1" class="card-actions">
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="removeExpense(index)"
                      class="ml-2"
                    ></v-btn>
                  </div>
                </div>
              </v-card-title>

              <v-card-text class="pt-0">
                <v-row>
                  <!-- Scope Selection -->
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="expense.scope"
                      :items="scopes"
                      item-title="name"
                      item-value="id"
                      label="Expense Scope"
                      :rules="[rules.scope]"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-account-group"
                    ></v-select>
                  </v-col>

                  <!-- Date Picker -->
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="expense.dateFormatted"
                      label="Date"
                      :rules="[rules.date]"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-calendar"
                      readonly
                      @click="openDatePicker(index)"
                      class="date-input"
                    >
                      <template v-slot:append-inner>
                        <v-btn
                          icon="mdi-calendar-today"
                          size="small"
                          variant="text"
                          @click="setCurrentDate(expense)"
                          class="today-btn"
                        ></v-btn>
                      </template>
                    </v-text-field>

                    <!-- Date Picker Dialog -->
                    <v-dialog
                      v-model="expense.showDatePicker"
                      max-width="320px"
                    >
                      <v-date-picker
                        v-model="expense.dateObject"
                        @update:model-value="updateDate(expense)"
                        show-adjacent-months
                        class="elevation-15"
                      ></v-date-picker>
                    </v-dialog>
                  </v-col>

                  <!-- Amount -->
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="expense.amount"
                      label="Amount"
                      :rules="[rules.amount]"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-currency-usd"
                      placeholder="0.00"
                      @input="formatAmount(expense, $event)"
                    ></v-text-field>
                  </v-col>

                  <!-- Merchant/Vendor -->
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="expense.merchant"
                      label="Merchant/Vendor"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-store"
                      placeholder="Where did you spend?"
                    ></v-text-field>
                  </v-col>

                  <!-- Category -->
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="expense.category"
                      :items="categories"
                      label="Category"
                      :rules="[rules.category]"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-tag"
                    ></v-select>
                  </v-col>

                  <!-- Notes -->
                  <v-col cols="12">
                    <v-textarea
                      v-model="expense.notes"
                      label="Notes (optional)"
                      variant="outlined"
                      density="comfortable"
                      rows="2"
                      prepend-inner-icon="mdi-note-text"
                      placeholder="Add any additional details..."
                    ></v-textarea>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </div>

          <!-- Action Buttons -->
          <div class="action-buttons-container">
            <v-row justify="center" class="mb-4">
              <v-col cols="auto">
                <v-btn
                  variant="outlined"
                  color="primary"
                  @click="addExpense"
                  prepend-icon="mdi-plus"
                  class="mx-2"
                >
                  Add Another
                </v-btn>
              </v-col>
              <v-col cols="auto">
                <v-btn
                  variant="outlined"
                  color="secondary"
                  @click="clearForm"
                  prepend-icon="mdi-refresh"
                  class="mx-2"
                >
                  Clear All
                </v-btn>
              </v-col>
            </v-row>

            <v-row justify="center">
              <v-col cols="auto">
                <v-btn
                  type="submit"
                  color="primary"
                  size="large"
                  :loading="loading"
                  :disabled="!canSubmit"
                  prepend-icon="mdi-content-save"
                  class="submit-btn"
                >
                  Save {{ expenses.length }} Expense{{ expenses.length !== 1 ? 's' : '' }}
                </v-btn>
              </v-col>
            </v-row>
        </div>
      </v-form>
    </v-container>
  </div>
</template>

<style scoped>
/* Main Layout */
.expense-input-container {
  background: transparent;
  width: 100%;
}

/* Expense Cards */
.expense-card-container {
  position: relative;
}

.expense-card {
  background-color: rgb(var(--v-theme-surface));
  border-radius: 12px;
  border: 1px solid rgba(var(--v-theme-outline), 0.2);
}

.expense-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: rgb(var(--v-theme-on-surface-variant));
}

.card-actions {
  display: flex;
  align-items: center;
}

/* Form Elements */
.date-input {
  cursor: pointer;
}

.date-input :deep(.v-field__input) {
  cursor: pointer;
}

.today-btn {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.today-btn:hover {
  opacity: 1;
}

/* Action Buttons */
.action-buttons-container {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(var(--v-theme-outline), 0.12);
}

.submit-btn {
  min-width: 200px;
  height: 48px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Responsive Design */
@media (max-width: 959px) {
  .content-box {
    padding: 20px;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .expense-card {
    margin-bottom: 16px;
  }
  
  .action-buttons-container {
    margin-top: 24px;
    padding-top: 16px;
  }
}

@media (max-width: 600px) {
  .page-background {
    padding: 16px;
  }
  
  .content-box {
    padding: 16px;
  }
  
  .section-title {
    font-size: 1.375rem;
    margin-bottom: 24px;
  }
  
  .expense-card {
    border-radius: 12px;
  }
  
  .submit-btn {
    min-width: 160px;
    width: 100%;
    max-width: 280px;
  }
}

/* Form Field Improvements */
:deep(.v-field--variant-outlined) {
  background-color: rgb(var(--v-theme-surface));
}

:deep(.v-field--variant-outlined .v-field__outline) {
  border-color: rgba(var(--v-theme-outline), 0.3);
}

:deep(.v-field--variant-outlined:hover .v-field__outline) {
  border-color: rgba(var(--v-theme-primary), 0.5);
}

:deep(.v-field--variant-outlined.v-field--focused .v-field__outline) {
  border-color: rgb(var(--v-theme-primary));
}

/* Loading and Disabled States */
.submit-btn:disabled {
  opacity: 0.6;
}

/* Success/Error Animations */
.v-alert {
  border-radius: 12px;
}
</style>
<script>
import { ref, onMounted, watch, computed } from 'vue';

export default {
    //nExpenseData prop added to edit existing expense
    props: {
    expenseData: {
      type: Object,
      default: null,
    },
  },
    setup(props,{emit}) {

        const loading = ref(false); // State to manage loading status

        // Retrieved from the backend server on mount
        const scopes = ref([]);
        const categories = ref([]);

        // Data structure to map names of people to that person's ID, according
        // to the backend server
       // const nameToIdMap = ref({});

        // Stores the response message and its type
        const responseMessage = ref({ message: '', type: '' });

        // Reference to the form element to reset form validation after submission
        const form = ref(null);

        // Initialize months first
        const months = ref(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']);
        
        // Helper function to format date for display
        function formatDateForDisplay(date) {
            if (!date) return '';
            return date.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
        
        // Helper function to create a new expense with default values
        function createNewExpense() {
            const today = new Date();
            return {
                scope: '',
                dateObject: today,
                dateFormatted: formatDateForDisplay(today),
                day: today.getDate(),
                month: months.value[today.getMonth()],
                year: today.getFullYear(),
                amount: '',
                category: '',
                merchant: '',
                notes: '',
                rowKey: Date.now(),
                ExpenseID: null,
                showDatePicker: false
            };
        }
        
        // Reference to expense data structure
        const expenses = ref([createNewExpense()]);
        
        //watch for changes in expenseData prop to populate the form
        watch(
            () => props.expenseData,
            (newVal) => {
                if (newVal) {
                    console.log('Received expenseData:', newVal);
                    const expenseDate = new Date(newVal.Year, months.value.indexOf(newVal.Month), newVal.Day);
                    expenses.value = [{
                        scope: newVal.ScopeID || '',
                        dateObject: expenseDate,
                        dateFormatted: formatDateForDisplay(expenseDate),
                        day: newVal.Day || '',
                        month: newVal.Month || '',
                        year: newVal.Year || '',
                        amount: newVal.Amount ? newVal.Amount.replace(/[^0-9.]/g, '') : '',
                        category: newVal.ExpenseCategory || '',
                        merchant: newVal.PlaidMerchantName || newVal.PlaidName || '',
                        notes: newVal.AdditionalNotes || '',
                        ExpenseID: newVal.ExpenseID,
                        showDatePicker: false
                    }];
                } else {
                    // If no expenseData, reset the form
                    expenses.value = [createNewExpense()];
                }
            },
            { immediate: true }
        );
        // Update fetchScopes to use the new API
        const fetchScopes = async () => {
        try {
            const response = await fetch('/api/get_scopes');
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            const data = await response.json();
            if (data.success) {
            // Transform scopes data for the dropdown
            scopes.value = data.scopes.map(scope => ({
                id: scope.id,
                name: `${scope.name} (${scope.type})`
            }));
            }
        } catch (error) {
            console.error('Error fetching scopes:', error);
        }
        };


        const fetchCategories = async () => {
            try {
                const response = await fetch('/api/get_categories');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                categories.value = data.categories;
            } catch (error) {
                console.error('Error fetching categories:', error);
                // Handle error, maybe set categories to default values or show an error message
            }
        };

        const rules = {
            required: value => !!value || 'Required.',
            scope: value => {
                return value !== null && value !== undefined && value !== '' || 'Please select a scope';
            },
            date: value => {
                return !!value || 'Please select a date';
            },
            amount: value => {
                if (!value) return 'Amount is required';
                const cleanValue = value.replace(/[^0-9.]/g, '');
                const numericValue = parseFloat(cleanValue);
                if (isNaN(numericValue)) return 'Please enter a valid amount';
                if (numericValue <= 0) return 'Amount must be greater than 0';
                if (!/^\d*\.?\d{0,2}$/.test(cleanValue)) return 'Amount can have at most 2 decimal places';
                return true;
            },
            category: value => {
                return value !== null && value !== undefined && value !== '' || 'Please select a category';
            },
        };
        
        // Computed property to check if form can be submitted
        const canSubmit = computed(() => {
            return expenses.value.every(expense => 
                expense.scope && 
                expense.dateFormatted && 
                expense.amount && 
                expense.category
            ) && !loading.value;
        });


        // Enhanced form management functions
        const addExpense = () => {
            const lastExpense = expenses.value[expenses.value.length - 1];
            const newExpense = createNewExpense();
            // Carry over scope from previous expense for convenience
            if (lastExpense.scope) {
                newExpense.scope = lastExpense.scope;
            }
            expenses.value.push(newExpense);
        };

        const removeExpense = (index) => {
            if (expenses.value.length > 1) {
                expenses.value.splice(index, 1);
            }
        };

        const clearForm = () => {
            expenses.value = [createNewExpense()];
            if (form.value) {
                form.value.reset();
            }
        };
        
        // Date picker functions
        const openDatePicker = (index) => {
            expenses.value[index].showDatePicker = true;
        };
        
        const updateDate = (expense) => {
            if (expense.dateObject) {
                expense.dateFormatted = formatDateForDisplay(expense.dateObject);
                expense.day = expense.dateObject.getDate();
                expense.month = months.value[expense.dateObject.getMonth()];
                expense.year = expense.dateObject.getFullYear();
            }
            expense.showDatePicker = false;
        };
        
        // Amount formatting function
        const formatAmount = (expense, event) => {
            let value = event.target.value;
            // Remove any non-numeric characters except decimal point
            value = value.replace(/[^0-9.]/g, '');
            // Ensure only one decimal point
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            // Limit to 2 decimal places
            if (parts[1] && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            expense.amount = value;
        };

        // Enhanced form validation
        const isFormValid = () => {
            for (let expense of expenses.value) {
                if (typeof rules.scope(expense.scope) === 'string' ||
                    typeof rules.date(expense.dateFormatted) === 'string' ||
                    typeof rules.amount(expense.amount) === 'string' ||
                    typeof rules.category(expense.category) === 'string') {
                    return false;
                }
            }
            return true;
        };

        const submitExpenses = async () => {
            try {

                // Check if form passes all validations
                if (!isFormValid()) {
                    console.log("Validation failed");
                    return;
                }

                loading.value = true; // Activate loading animation

                // If expenses are not "Joint", send the PersonID instead of the PersonName
                // as the Expense Scope. This avoids having to do this on the backend.
                const modifiedExpenses = expenses.value.map(expense => ({
                    ...expense,
                    scopeId: expense.scope // scope is already the ID from the v-select
                }));

                //Defining variables for response
                let url = '/api/submit_expenses';
                let method = 'POST';

                // Check if we're editing an existing expense
                if (modifiedExpenses[0].ExpenseID) {
                url = '/api/update_expense';
                method = 'PUT';
                }

                const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expenses: modifiedExpenses }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const responseData = await response.json();
                console.log('Server response:', responseData);
                
                if (responseData.success) {
                    expenses.value = [createNewExpense()]; // Clear the form with fresh expense
                    responseMessage.value = { message: responseData.message, type: 'success' };

                    if (form.value) {
                        form.value.reset(); // Reset the form validation
                    }
                    
                    // Auto-hide success message after 5 seconds
                    setTimeout(() => {
                        responseMessage.value = { message: '', type: '' };
                    }, 5000);
                    
                    //New emit for updating expenses
                    emit('update-expenses');
                } else {
                    responseMessage.value = { message: responseData.error, type: 'error' };
                }

            } catch (error) {
                console.error('Error submitting expenses:', error);
                responseMessage.value = { message: 'Failed to submit expenses. Please try again.', type: 'error' };
            } finally {
                loading.value = false; // Deactivate loading animation
            }
        };

        onMounted(() => {
            fetchScopes();
            fetchCategories();
        });

        // Enhanced current date function
        function setCurrentDate(expense) {
            const today = new Date();
            expense.dateObject = today;
            expense.dateFormatted = formatDateForDisplay(today);
            expense.day = today.getDate();
            expense.month = months.value[today.getMonth()];
            expense.year = today.getFullYear();
        }

        return { 
            expenses,
            scopes, 
            months,
            categories, 
            rules, 
            loading,
            responseMessage,
            form,
            canSubmit,
            addExpense,
            removeExpense,
            clearForm,
            openDatePicker,
            updateDate,
            formatAmount,
            submitExpenses,
            setCurrentDate,
            formatDateForDisplay,
            createNewExpense,
        };
    }
};
</script>