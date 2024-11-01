<template>
    <v-container class="rounded-box-embed">
        <h2 class="expenses-header text-center">Input New Expenses</h2>

        <!-- Response Message -->
        <div v-if="responseMessage.message" :class="{'text-success': responseMessage.type === 'success', 'text-error': responseMessage.type === 'error'}">
            {{ responseMessage.message }}
        </div>

        <v-form ref="form" id="expensesForm" @submit.prevent="submitExpenses">
            <!-- Desktop view -->
            <div class="d-none d-md-block">
                <v-table dense class="elevation-1 tight-table">
                    <thead>
                    <tr>
                        <th class="column-scope">Scope</th>
                        <th class="column-day">Day</th>
                        <th class="column-month">Month</th>
                        <th class="column-year">Year</th>
                        <th class="column-amount">Amount</th>
                        <th class="column-category">Category</th>
                        <th class="column-notes">Notes</th>
                        <th class="column-set-date">Today</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="(expense, index) in expenses" :key="`row-${index}-${expense.rowKey}`">
                        <!-- Expense Scope Dropdown -->
                        <td>
                            <v-select
                            v-model="expense.scope"
                            :items="scopes"
                            item-title="name"
                            item-value="id"
                            label="Select Scope"
                            :rules="[rules.scope]"
                            class="input-field input-field--scope"
                            ></v-select>
                        </td>
                        <!-- Day Field -->
                        <td>
                            <v-text-field
                            v-model="expense.day"
                            type="number"
                            :rules="[rules.day]"
                            class="input-field input-field--day"
                            hide-spin-buttons
                            ></v-text-field>
                        </td>
                        <!-- Month Dropdown -->
                        <td>
                        <v-select
                            v-model="expense.month"
                            :items="months"
                            :rules="[rules.month]"
                            class="input-field input-field--month"
                        ></v-select>
                        </td>
                        <!-- Year Field -->
                        <td>
                            <v-text-field
                            v-model="expense.year"
                            type="number"
                            :rules="[rules.year]"
                            class="input-field input-field--year"
                            hide-spin-buttons
                            ></v-text-field>
                        </td>
                        <!-- Amount Field -->
                        <td>
                            <v-text-field
                            v-model="expense.amount"
                            type="text"
                            :rules="[rules.amount]"
                            class="input-field input-field--amount"
                            :prepend-inner-icon="'mdi-currency-usd'"
                            ></v-text-field>
                        </td>
                        <!-- Expense Category Dropdown -->
                        <td>
                        <v-select
                            v-model="expense.category"
                            :items="categories"
                            :rules="[rules.category]"
                            class="input-field input-field--category"
                        ></v-select>
                        </td>
                        <!-- Additional Notes Field -->
                        <td>
                        <v-text-field
                            v-model="expense.notes"
                            class="input-field input-field--notes"
                        ></v-text-field>
                        </td>
                        <td class="today-button-cell">
                            <v-btn 
                                small 
                                @click="setCurrentDate(expense)"
                                class="today-btn"
                                density="compact"
                            >Today</v-btn>
                        </td>
                    </tr>
                </tbody>
                </v-table>
            </div>

            <!-- Mobile view -->
            <div class="d-md-none">
                <div v-for="(expense, index) in expenses" :key="`row-mobile-${index}-${expense.rowKey}`" class="mobile-expense-form">
                    <v-select
                        v-model="expense.scope"
                        :items="scopes"
                        item-title="name"
                        item-value="id"
                        label="Select Scope"
                        :rules="[rules.scope]"
                        class="mb-2"
                    ></v-select>

                    <div class="date-fields">
                        <v-text-field
                            v-model="expense.day"
                            type="number"
                            label="Day"
                            :rules="[rules.day]"
                            class="date-field"
                            hide-spin-buttons
                        ></v-text-field>

                        <v-select
                            v-model="expense.month"
                            :items="months"
                            label="Month"
                            :rules="[rules.month]"
                            class="date-field"
                        ></v-select>

                        <v-text-field
                            v-model="expense.year"
                            type="number"
                            label="Year"
                            :rules="[rules.year]"
                            class="date-field"
                            hide-spin-buttons
                        ></v-text-field>

                        <v-btn small @click="setCurrentDate(expense)" class="today-btn">Today</v-btn>
                    </div>

                    <v-text-field
                        v-model="expense.amount"
                        type="text"
                        label="Amount"
                        :rules="[rules.amount]"
                        :prepend-inner-icon="'mdi-currency-usd'"
                        class="mb-2"
                    ></v-text-field>

                    <v-select
                        v-model="expense.category"
                        :items="categories"
                        label="Category"
                        :rules="[rules.category]"
                        class="mb-2"
                    ></v-select>

                    <v-text-field
                        v-model="expense.notes"
                        label="Notes"
                        class="mb-2"
                    ></v-text-field>

                    <v-divider class="my-4"></v-divider>
                </div>
            </div>

            <v-row justify="center" class="button-row">
                <v-col cols="auto">
                    <v-btn class="mx-2" type="button" @click="addRow">Add Row</v-btn>
                </v-col>
                <v-col cols="auto">
                    <v-btn class="mx-2" type="button" @click="deleteRow">Delete Last Row</v-btn>
                </v-col>
                <v-col cols="auto">
                    <v-btn class="mx-2" type="button" @click="clearLastRow">Clear Last Row</v-btn>
                </v-col>
                <v-col cols="auto">
                    <v-btn class="mx-2" 
                    type="submit" 
                    color="primary"
                    :loading="loading"
                    >Submit</v-btn>
                </v-col>
            </v-row>
        </v-form>
    </v-container>
</template>

<style scoped>
.expenses-header {
    margin-bottom: 20px;
}

.tight-table {
    table-layout: fixed;
    width: 100%;
    border-radius: 12px;
}

/* Column width definitions for desktop view */
.column-scope { width: 20%; }
.column-day { width: 8%; }
.column-month { width: 12%; }
.column-year { width: 8%; }
.column-amount { width: 12%; }
.column-category { width: 20%; }
.column-notes { width: 15%; }
.column-set-date { width: 5%; }

.text-success {
    color: darkgreen;
}

.text-error {
    color: red;
}

/* Tight spacing for table cells */
.tight-table th,
.tight-table td {
    padding: 4px 8px !important;
}

/* Input field styles */
.input-field {
    margin: 0;
    padding: 4px 0;
}

/* Prevent input fields from growing too large 
.input-field :deep(.v-field__input) {
    min-height: 32px !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
} */

/* Mobile view styles */
.mobile-expense-form {
    margin-bottom: 16px;
    padding: 16px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}

.date-fields {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
    gap: 8px;
    margin-bottom: 16px;
}

.date-field {
    min-width: 70px;
}

.today-button-cell {
    vertical-align: middle;
    height: 100%;
    padding-top: 12px !important; /* Adjust based on your specific needs */
    margin: 0;
    /* Ensure the button height matches other elements */
    height: 32px;
}

.today-btn {
    align-self: center;
    height:40px;
    margin-bottom:15px;
}

/* Button row spacing */
.button-row {
    margin-top: 16px;
}

/* Rounded box styling */
.rounded-box-embed {
    background-color: #ffffffe3;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Utility classes */
.mb-2 {
    margin-bottom: 8px;
}

.my-4 {
    margin-top: 16px;
    margin-bottom: 16px;
}


</style>
<script>
import { ref, onMounted, watch } from 'vue';

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

        // Reference to a single row in the submit expenses row.
        // rowKey property is used to reset form validation when clearing a row of its data
        const expenses = ref([{ 
            scope: '', day: '', month: '', year: '', amount: '', category: '', notes: '', 
            rowKey: 0 ,ExpenseID: null,
        }]);
        const months = ref(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']);
        
        //watch for changes in expenseData prop to populate the form
        watch(
      () => props.expenseData,
      (newVal) => {
        if (newVal) {
            console.log('Received expenseData:', newVal);
          expenses.value = [{
            scope: newVal.ScopeID || '',
            day: newVal.Day || '',
            month: newVal.Month || '',
            year: newVal.Year || '',
            amount: newVal.Amount ? newVal.Amount.replace(/[^0-9.]/g, '') : '',
            category: newVal.ExpenseCategory || '',
            notes: newVal.AdditionalNotes || '',
            ExpenseID: newVal.ExpenseID,
          }];
        }
        else {
          // If no expenseData, reset the form
          expenses.value = [
            {
              scope: '',
              day: '',
              month: '',
              year: '',
              amount: '',
              category: '',
              notes: '',
              rowKey: 0,
              ExpenseID: null,
            },
          ];
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
                return value !== null && value !== undefined && value !== '' || 'Scope is required';
            },
            day: value => {
                if (!value) return 'Day is required';
                if (isNaN(value)) return 'Day must be a number';
                return (value >= 1 && value <= 31) || 'Day must be between 1 and 31';
            },
            month: value => {
                if (!value) return 'Month is required';
                return months.value.includes(value) || 'Invalid month selected';
            },
            year: value => {
                if (!value) return 'Year is required';
                if (isNaN(value)) return 'Year must be a number';
                return (value >= 2000 && value <= 2050) || 'Year must be between 2000 and 2050';
            },
            amount: value => {
                if (!value) return 'Amount is required';
                const numericValue = parseFloat(value);
                if (isNaN(numericValue)) return 'Amount must be a valid number';
                if (numericValue < 0) return 'Amount cannot be negative';
                if (!/^\d*\.?\d{0,2}$/.test(value)) return 'Amount must be a non-negative number with at most two decimal places';
                return true;
            },
            category: value => {
                return value !== null && value !== undefined && value !== '' || 'Expense Category is required';
            },
        };


        const addRow = () => {
        const lastExpense = expenses.value[expenses.value.length - 1];
        expenses.value.push({ 
            scope: lastExpense.scope, 
            day: '', 
            month: lastExpense.month, 
            year: lastExpense.year, 
            amount: '', 
            category: '', 
            notes: '' 
        });
        };

        const deleteRow = () => {
            if (expenses.value.length > 1) {
                expenses.value.pop();
            }
        };

        const clearLastRow = () => {
            const lastExpenseIndex = expenses.value.length - 1;
            if (lastExpenseIndex >= 0) {
                expenses.value[lastExpenseIndex] = { 
                scope: '', day: '', month: '', year: '', amount: '', category: '', notes: '',
                rowKey: expenses.value[lastExpenseIndex].rowKey + 1
                };
            }
        };

        // Custom validation method for the form, because built-in Vuetify's validate()
        // method does not work with v-for
        const isFormValid = () => {
            for (let expense of expenses.value) {
                // Check each rule; if the rule returns a string (error message), it means validation failed
                if (typeof rules.required(expense.scope) === 'string' ||
                    typeof rules.day(expense.day) === 'string' ||
                    typeof rules.year(expense.year) === 'string' ||
                    typeof rules.amount(expense.amount) === 'string') {
                    // Validation failed
                    return false;
                }
            }
            // All validations passed
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
                    expenses.value = [{ scope: '', day: '', month: '', year: '', amount: '', category: '', notes: '' }]; // Clear the form
                    responseMessage.value = { message: responseData.message, type: 'success' };

                    if (form.value) {
                        form.value.reset(); // Reset the form validation
                    }
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

        //current date function
         function setCurrentDate(expense) {
            const today = new Date();
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
            addRow, 
            deleteRow, 
            clearLastRow,
            submitExpenses,
            setCurrentDate,
        };
    }
};
</script>