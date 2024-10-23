<template>
  <v-container class="container-10col">
    <v-row justify="center" class="hero-container">
      <v-col cols="5" md="5" class="text-left" style=" padding: 0 10% 0 10%;">
        <h1 class="display-1 hero-header">Where did all your money go?</h1>
        <p class="subtitle-1 hero-paragraph">
          Get insights into your expenses, and how much you spend on your next trip.
        </p>
        <v-btn large color="primary" to="/signup" class="cta-button">
          Get Started
        </v-btn>
      </v-col>
      <v-col cols="5" md="5" class="d-flex justify-center">
        <v-img src="@/assets/appScreenshot.png" class="hero-image"></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
  .hero-container {
    min-height: 80vh; /* Adjust this value to change the overall spacing */
    margin-top: -6rem;
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
  max-width: 80%; /* Adjust this value to set the maximum width of the image */
  max-height: 500px; /* Adjust this value to set the maximum height of the image */
  height: auto; /* Maintain aspect ratio */
  margin-top: 0rem; /* Space between image and button */
  display: block; /* To ensure it's a block level element */
  margin-left: auto; /* Align to center */
  margin-right: auto; /* Align to center */
    /* New styles */
    border-radius: 12px; /* Rounds the corners of the image */
  border: 2px solid #ddd; /* Simple border with a light grey color */
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.3); /* Adds a shadow to the bottom right */
}
</style>