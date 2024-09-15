<template>
    <v-container>
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
        <v-btn color="red" @click="deleteSelectedExpenses" v-if="selected.length > 0">
          <v-icon left>mdi-trash-can</v-icon>
          Delete Selected
        </v-btn>

        <v-data-table v-else
        :headers="headers"
        :items="expenses"
        :search="search"
        item-value="ExpenseID"
        class="elevation-1"
        density="compact"
        :no-data-text="'No expenses found'"
        items-per-page="25"
        show-select
        v-model:selected="selected"
        ></v-data-table>
    </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {

    const loading = ref(true);  // Indicates whether data is being fetched
    const search = ref("");  // Reactive property for search query
    
    const expenses = ref([]);
    const headers = ref([
    { title: 'Select', value: 'data-table-select', sortable: false },
    { 
        title: 'Scope', 
        align: 'start', 
        value: 'PersonName',
        sortable: true
    },
      { title: 'Expense Date', value: 'ExpenseDate', sortable: true },
      { title: 'Amount', value: 'Amount' },
      { title: 'Expense Category', value: 'ExpenseCategory', sortable: true },
      { title: 'Additional Notes', value: 'AdditionalNotes', sortable: true }
    ]);

    const selected = ref([]);  // To store selected expenses

    const fetchExpenses = async () => {

      loading.value = true; // Start loading
      
      try {
        const response = await fetch('/api/get_expenses');
        
        if (!response.ok) {
          throw new Error('Failed to fetch expenses');
        }
        const data = await response.json();

        console.log('API Response:', data); // Log the response

        if (data.success) {
          expenses.value = data.expenses;
        }

        loading.value = false; // Stop loading after data is fetched
      } catch (error) {
        console.error('Error:', error);
        loading.value = false; // Stop loading if there is an error
      }
    };

    const deleteSelectedExpenses = async () => {
      if (selected.value.length === 0) {
        return;
      }
      
      try {
        const response = await fetch('/api/delete_expenses', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            expenseIds: selected.value.map(expense => expense.ExpenseID), // Delete using ExpenseID key
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to delete expenses');
        }

        const data = await response.json();
        if (data.success) {
          // Remove deleted expenses from the list
          expenses.value = expenses.value.filter(expense => !selected.value.includes(expense));
          selected.value = []; // Clear the selection after deletion
        }
      } catch (error) {
        console.error('Error:', error);
      }
    };

    onMounted(() => {
      fetchExpenses();
    });

    return { loading, search, expenses, headers };
  }
};
</script>