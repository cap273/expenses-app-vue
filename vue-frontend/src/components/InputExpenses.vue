<template>
    <v-container>
        <h2 class="expenses-header text-center">Input New Expenses</h2>

        <!-- Response Message -->
        <div v-if="responseMessage.message" :class="{'text-success': responseMessage.type === 'success', 'text-error': responseMessage.type === 'error'}">
            {{ responseMessage.message }}
        </div>

        <v-form ref="form" id="expensesForm" @submit.prevent="submitExpenses">
            <v-table dense class="elevation-1 tight-table">
                <thead>
                <tr>
                    <th class="column-scope">Expense Scope</th>
                    <th class="column-day">Day</th>
                    <th class="column-month">Month</th>
                    <th class="column-year">Year</th>
                    <th class="column-amount">Amount</th>
                    <th class="column-category">Expense Category</th>
                    <th class="column-notes">Additional Notes</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(expense, index) in expenses" :key="index">
                    <!-- Expense Scope Dropdown -->
                    <td>
                    <v-select
                        v-model="expense.scope"
                        :items="scopes"
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
                    <!-- Changed to type=text to better handle decimal places.-->
                    <td>
                        <v-text-field
                        v-model="expense.amount"
                        type="text"
                        :rules="[rules.amount]"
                        class="input-field .input-field--amount"
                        :prepend-inner-icon="'mdi-currency-usd'"
                        ></v-text-field>
                    </td>
                    <!-- Expense Category Dropdown -->
                    <td>
                    <v-select
                        v-model="expense.category"
                        :items="categories"
                        class="input-field .input-field--category"
                    ></v-select>
                    </td>
                    <!-- Additional Notes Field -->
                    <td>
                    <v-text-field
                        v-model="expense.notes"
                        class="input-field .input-field--additionalnotes"
                    ></v-text-field>
                    </td>
                </tr>
            </tbody>
            </v-table>
            <v-row justify="center" class="button-row">
                <v-col cols="auto">
                    <v-btn class="mx-2" type="button" @click="addRow">Add Row</v-btn>
                </v-col>
                <v-col cols="auto">
                    <v-btn class="mx-2" type="button" @click="deleteRow">Delete Last Row</v-btn>
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

<script>
import { ref, onMounted } from 'vue';

export default {
    setup() {

        const loading = ref(false); // State to manage loading status

        // Retrieved from the backend server on mount
        const scopes = ref([]);
        const categories = ref([]);

        // Data structure to map names of people to that person's ID, according
        // to the backend server
        const nameToIdMap = ref({});

        // Stores the response message and its type
        const responseMessage = ref({ message: '', type: '' });

        // Reference to the form element to reset form validation after submission
        const form = ref(null);

        const fetchScopes = async () => {
            try {
                const response = await fetch('/api/get_persons');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json(); 

                // Create the mapping from PersonName to PersonID
                nameToIdMap.value = data.reduce((map, person) => {
                    map[person.PersonName] = person.PersonID;
                    return map;
                }, {});

                // Populate scopes based on the number of persons
                if (data.length === 1) {
                    // If there's only one person, use their name
                    scopes.value = [data[0].PersonName];
                } else if (data.length > 1) {
                    // If there are multiple persons, add "Joint" and each person's name
                    scopes.value = ['Joint', ...data.map(person => person.PersonName)];
                }
            } catch (error) {
                console.error('Error fetching scopes:', error);
                // Handle error, maybe set scopes to default values or show an error message
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
            day: value => {
                if (!value) return 'Day is required';
                if (isNaN(value)) return 'Day must be a number';
                return (value >= 1 && value <= 31) || 'Day must be between 1 and 31';
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
                if (!/^[0-9]*\.?[0-9]{0,2}$/.test(value)) return 'Amount must be a number with at most two decimal places';
                return true;
            }
        };

        const expenses = ref([{ scope: '', day: '', month: '', year: '', amount: '', category: '', notes: '' }]);
        const months = ref(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']);
        
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

        const submitExpenses = async () => {
            try {
                loading.value = true; // Activate loading animation

                // If expenses are not "Joint", send the PersonID instead of the PersonName
                // as the Expense Scope. This avoids having to do this on the backend.
                const modifiedExpenses = expenses.value.map(expense => ({
                    ...expense,
                    scope: expense.scope === 'Joint' ? 'Joint' : nameToIdMap.value[expense.scope]
                }));

                const response = await fetch('/api/submit_expenses', {
                    method: 'POST',
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
            submitExpenses
        };
    }
};
</script>

<style scoped>

.expenses-header {
  margin-bottom: 20px;
}

.expenses-header {
  margin-bottom: 20px;
}

.button-row {
  margin-top: 20px;
}

.tight-table {
  table-layout: fixed;
  width: 100%;
}

.text-success {
    color: darkgreen;
  }

.text-error {
    color: red;
}

</style>
