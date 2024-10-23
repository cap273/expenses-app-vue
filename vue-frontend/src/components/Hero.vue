<template>
  <v-container class="container-compact">
    <v-row justify="center" class="hero-container">
      <!-- Left Column -->
      <v-col
        cols="12"
        md="6"
        class="d-flex flex-column justify-start align-start px-4"
      >
        <div class="text-content">
          <h1 class="display-1 hero-header">
            Where did all your money go?
          </h1>
          <p class="subtitle-1 hero-paragraph">
            Get insights into your expenses, and how much you spend on your next trip.
          </p>
          <v-btn
            large
            color="primary"
            to="/signup"
            class="cta-button"
          >
            Get Started
          </v-btn>
        </div>
      </v-col>

      <!-- Right Column -->
      <v-col
        cols="12"
        md="6"
        class="d-flex justify-center align-center px-4"
      >
        <v-img
          src="@/assets/appScreenshot.png"
          class="hero-image"
        ></v-img>
      </v-col>
    </v-row>
  </v-container>

  <div class="customer-quotes-container">
  <v-container fluid style="max-width: 1400px;">
    <v-row>
      <!-- First Quote -->
      <v-col cols="12" md="6" class="quote-column">
        <div class="quote-card">
          <div class="star-rating">
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
          </div>
          <p>"This app completely changed how I track my expenses. Highly recommended!"</p>
          <p><strong>- Carlos P.</strong></p>
        </div>
      </v-col>

      <!-- Second Quote -->
      <v-col cols="12" md="6" class="quote-column">
        <div class="quote-card">
          <div class="star-rating">
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
            <v-icon small color="yellow darken-2">mdi-star</v-icon>
          </div>
          <p>"A must-have tool for anyone wanting to get a grip on their finances."</p>
          <p><strong>- Janusz G.</strong></p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</div>

</template>

<style scoped>

.container-compact {
  max-width: 1400px; /* Reduce the container width to make it more compact */
  margin: 0 auto; /* Center the container */
  padding-left: 16px; /* Add padding to prevent content touching the edges */
  padding-right: 16px;
}

.hero-container {
  min-height: 60vh;
  margin-top: 0rem;
  align-items: center;
  justify-content: center;
}

.hero-header {
  font-size: 3rem;
  font-family: 'Arial', sans-serif;
  max-width: 400px
}

.hero-paragraph {
  max-width: 400px; /* Limit the width of the text content */
  color: #757575;
  font-family: 'Arial', sans-serif;
  margin-bottom: 2rem;
}

.hero-image {
  max-width: 100%;
  max-height: 500px;
  height: auto;
  display: block;
  margin-left: auto;
  margin-right: auto;
  border-radius: 12px;
  border: 2px solid #ddd;
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.3);
}

/* New styles for customer quotes */
.customer-quotes-container {
    background-color: #f5f5f5; /* Light grey background */
    padding: 2rem 0;
  }

  .quote-column {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .quote-card {
    max-width: 500px;
    margin: 1rem;
    background-color: transparent;
    text-align: center;
    font-size: 1.2rem;
  }

  .star-rating {
    display: flex;
    justify-content: center;
    margin-bottom: 0.5rem;
  }

  .star-rating v-icon {
    margin-right: 2px;
  }

</style>