<template>
  <v-container>
    <v-row justify="center" class="hero-container">
      <v-col cols="12" class="text-center">
        <h1 class="display-1 hero-header">Take control of your financial life</h1>
        <p class="subtitle-1 hero-paragraph">With Expenses App, record and analyze your personal or household expenses like a CFO.</p>
        <v-btn large color="primary" to="/signup">Get started</v-btn>
        <v-img src="@/assets/hero.png" class="hero-image"></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
  .hero-container {
    min-height: 80vh; /* Adjust this value to change the overall spacing */
    align-items: center; /* Center vertically in the container */
    justify-content: center; /* Center horizontally */
  }

  .hero-header {
    font-size: 3rem; /* Larger font size for the header */
    font-family: 'Arial', sans-serif; /* Change to your preferred font */
  }

  .hero-paragraph {
    color: #757575; /* Middle grey color */
    font-family: 'Arial', sans-serif; /* Match header font */
    margin-bottom: 2rem; /* Space between paragraph and button */
  }
  .hero-image {
  max-width: 50%; /* Adjust this value to set the maximum width of the image */
  max-height: 300px; /* Adjust this value to set the maximum height of the image */
  height: auto; /* Maintain aspect ratio */
  margin-top: 2rem; /* Space between image and button */
  display: block; /* To ensure it's a block level element */
  margin-left: auto; /* Align to center */
  margin-right: auto; /* Align to center */
}
</style>