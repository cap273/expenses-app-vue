<!-- src/components/Table.vue -->
<template>
  <Identity v-if="isIdentity" :data="data" :categories="categories" />
  <table v-else class="dataTable">
    <thead class="header">
      <tr class="headerRow">
        <th v-for="(category, index) in categories" :key="index" class="headerField">
          {{ category.title }}
        </th>
      </tr>
    </thead>
    <tbody class="body">
      <tr v-for="(item, index) in limitedData" :key="index" class="dataRows">
        <td
          v-for="(category, colIndex) in categories"
          :key="colIndex"
          class="dataField"
        >
          {{ item[category.field] }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import Identity from './Identity.vue';

export default {
  name: 'Table',
  components: {
    Identity,
  },
  props: {
    data: {
      type: Array,
      required: true,
    },
    categories: {
      type: Array,
      required: true,
    },
    isIdentity: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    limitedData() {
      // Limit the number of rows to 15
      return this.data.slice(0, 15);
    },
  },
};
</script>

<style scoped>
.dataTable {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.headerRow {
  background-color: #f2f2f2;
}

.headerField {
  padding: 8px;
  border: 1px solid #ddd;
  font-weight: bold;
}

.dataRows {
  border-bottom: 1px solid #ddd;
}

.dataField {
  padding: 8px;
  border: 1px solid #ddd;
}
</style>
