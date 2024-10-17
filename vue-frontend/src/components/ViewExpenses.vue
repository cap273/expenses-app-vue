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
      <v-btn color="red" @click="deleteSelectedExpenses" >
        <v-icon left>mdi-trash-can</v-icon>
        Delete 
      </v-btn> 
      <!--  <v-btn color="blue" @click="editExpense(item)">
        <v-icon left>mdi-pencil</v-icon>
        Edit
      </v-btn>  -->
     

            <v-data-table
        :headers="headers"
        :items="expenses"
        :search="search"
        class="elevation-1"
        item-value="ExpenseID"
        density="compact"
        :no-data-text="'No expenses found'"
        items-per-page="25"
        show-select
        v-model="selected"
      >
        <!-- Scoped Slot for Actions Column -->
        <template v-slot:item.actions="{ item }">
          <v-btn color="blue" @click="editExpense(item)">
            <v-icon left>mdi-pencil</v-icon>
            Edit
          </v-btn>
        </template>
      </v-data-table>

        <!-- Edit Expense Dialog -->
        <v-dialog v-model="isEditDialogOpen" max-width="1200px">
          <template v-slot:default="dialog">
            <v-card>
              <v-toolbar color="primary" dark>
                <v-toolbar-title>Edit Expense</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon @click="isEditDialogOpen = false">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-toolbar>
              <v-card-text>
                <input-expenses
                  :expenseData="selectedExpense"
                  @update-expenses="handleUpdateExpenses"
                />
              </v-card-text>
            </v-card>
          </template>
        </v-dialog>
      

  </v-container>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import InputExpenses from './InputExpenses.vue';

export default {
  components: {
    InputExpenses,
  },
  setup() {
    const loading = ref(true);
    const search = ref("");
    const expenses = ref([]);
    const headers = ref([
      { title: 'Scope', align: 'start', value: 'PersonName', sortable: true },
      { title: 'Expense Date', value: 'ExpenseDate', sortable: true },
      { title: 'Amount', value: 'Amount' },
      { title: 'Expense Category', value: 'ExpenseCategory', sortable: true },
      { title: 'Additional Notes', value: 'AdditionalNotes', sortable: true },
      { title: 'Actions', value: 'actions', sortable: false },
    ]);

    const selected = ref([]); // This now holds ExpenseID values

    const fetchExpenses = async () => {
      loading.value = true;
      try {
        const response = await fetch('/api/get_expenses');
        if (!response.ok) throw new Error('Failed to fetch expenses');

        const data = await response.json();
        console.log('API Response:', data);

        if (data.success) {
          expenses.value = data.expenses;
          console.log('Expenses fetched:', expenses.value);
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        loading.value = false;
      }
    };

    const deleteSelectedExpenses = async () => {
      if (selected.value.length === 0) {
        console.log("No expenses selected");
        return;
      }

      console.log("Selected Expense IDs:", selected.value); // Log the selected ExpenseIDs

      try {
        const body = JSON.stringify({ expenseIds: selected.value });

        const response = await fetch("/api/delete_expenses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
        });

        if (!response.ok) {
          throw new Error("Failed to delete expenses");
        }

        const data = await response.json();
        if (data.success) {
          // Remove deleted expenses from the list based on ExpenseID
          expenses.value = expenses.value.filter(
            expense => !selected.value.includes(expense.ExpenseID)
          );
          selected.value = []; // Clear the selection after deletion
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    // Watch for changes in `selected` to debug selection behavior
    watch(selected, (newVal) => {
      console.log("Updated selected items (via watch):", newVal);
    });

    // New constants for editing expenses
    const isEditDialogOpen = ref(false);
    const selectedExpense = ref(null);
    const editExpense = (expense) => {
      console.log('Editing expense:', expense);
      selectedExpense.value = expense;
      isEditDialogOpen.value = true;
    };
    const handleUpdateExpenses = () => {
      fetchExpenses();
      isEditDialogOpen.value = false;
    };

    onMounted(fetchExpenses);

    return {
      loading,
      search,
      expenses,
      headers,
      selected,
      deleteSelectedExpenses,
      isEditDialogOpen,
      selectedExpense,
      editExpense,
      handleUpdateExpenses,
    };
  },
};
</script>
