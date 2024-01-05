<template>
    <v-container>
        <v-text-field
        v-model="search"
        label="Search"
        class="mb-3"
        ></v-text-field>

        <v-data-table
        :headers="headers"
        :items="expenses"
        :search="search"
        class="elevation-1"
        density="compact"
        :no-data-text="'No expenses found'"
        items-per-page="25"
        ></v-data-table>
    </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {

    const search = ref("");  // Reactive property for search query
    
    const expenses = ref([]);
    const headers = ref([
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

    const fetchExpenses = async () => {
      try {
        const response = await fetch('/api/get_expenses');
        if (!response.ok) {
          throw new Error('Failed to fetch expenses');
        }
        const data = await response.json();
        if (data.success) {
          expenses.value = data.expenses;
        }
      } catch (error) {
        console.error('Error:', error);
      }
    };

    onMounted(() => {
      fetchExpenses();
    });

    return { search, expenses, headers };
  }
};
</script>