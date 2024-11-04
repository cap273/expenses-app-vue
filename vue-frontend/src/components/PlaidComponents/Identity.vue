<!-- src/components/Identity.vue -->
<template>
  <div class="identityTable">
    <div class="identityHeadersRow">
      <span v-for="(category, index) in categories" :key="index" class="identityHeader">
        {{ category.title }}
      </span>
    </div>
    <div class="identityDataBody">
      <div v-for="(item, rowIndex) in data" :key="rowIndex" class="identityDataRow">
        <span
          v-for="(category, colIndex) in categories"
          :key="colIndex"
          class="identityDataField"
        >
          {{ item[category.field] }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Identity',
  props: {
    data: {
      type: Array,
      required: true,
    },
    categories: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped>
.identityTable {
  width: 90%;
  margin-bottom: 30px;
  font-size: 1.4rem;
  line-height: normal;
}

.identityHeadersRow {
  display: grid;
  grid-template-columns: repeat(4, 25%);
  gap: 10px;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #000;
  font-weight: bold;
}

.identityHeader {
  line-height: 20px;
  padding: 10px 0 4px 0;
}

.identityDataBody {
  margin-top: 20px;
}

.identityDataRow {
  display: grid;
  grid-template-columns: repeat(4, 25%);
  word-wrap: break-word;
  gap: 10px;
  margin-bottom: 5px;
}
</style>
