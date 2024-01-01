<template>
  <v-container>
    <v-btn @click="fetchMessage">Fetch Message</v-btn>
    <p>{{ message }}</p>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      message: ''
    };
  },
  methods: {
    async fetchMessage() {
      try {
        const response = await fetch('/api/hello');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        this.message = data.message;
      } catch (error) {
        console.error("There was a problem with the fetch operation:", error);
      }
    }
  }
};
</script>