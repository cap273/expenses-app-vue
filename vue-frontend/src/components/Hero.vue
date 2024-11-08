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
            Simple, big picture, expense tracking
          </h1>
          <p class="subtitle-1 hero-paragraph">
            Get insights into your expenses and find out how much you can spend on that next vacation.
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


  <!-- New Features Section -->
  <v-container class="features-container" id="features">
    <!-- Feature 1 -->
    <v-row class="align-center feature-row">
      <!-- Left Column: Text Content -->
      <v-col
        cols="12"
        md="6"
        class="d-flex flex-column justify-center align-center px-4"
      >
        <div class="feature-text">
          <h2 class="feature-title">Figure out where all your money went</h2>
          <p class="feature-description">
            Track your expenses effortlessly and get detailed insights.
          </p>
        </div>
      </v-col>

      <!-- Right Column: Image -->
      <v-col
        cols="12"
        md="6"
        class="d-flex justify-center align-center px-4"
      >
        <v-img
          src="@/assets/appScreenshot.png"
          alt="Feature 1 Image"
          class="feature-image"
        ></v-img>
      </v-col>
    </v-row>

    <!-- Feature 2 (Image Left, Text Right) -->
    <v-row class="align-center feature-row flex-row-reverse">
      <v-col
        cols="12"
        md="6"
        class="d-flex flex-column justify-center align-center px-4"
      >
        <div class="feature-text">
          <h2 class="feature-title">
            Plan for your next big purchase or vacation
          </h2>
          <p class="feature-description">
            Create budgets and save towards your goals with ease.
          </p>
        </div>
      </v-col>
      <!-- Left Column: Image -->
      <v-col
        cols="12"
        md="6"
        class="d-flex justify-center align-start px-4"
      >
        <v-img
          src="@/assets/appScreenshot.png"
          alt="Feature 2 Image"
          class="feature-image"
        ></v-img>
      </v-col>

      <!-- Right Column: Text Content -->

    </v-row>

    <!-- Feature 3 -->
    <v-row class="align-center feature-row">
      <!-- Left Column: Text Content -->
      <v-col
        cols="12"
        md="6"
        class="d-flex flex-column justify-center align-center px-4"
      >
        <div class="feature-text">
          <h2 class="feature-title">Keep track of household expenses</h2>
          <p class="feature-description">
            Manage shared expenses and stay on top of bills.
          </p>
        </div>
      </v-col>

      <!-- Right Column: Image -->
      <v-col
        cols="12"
        md="6"
        class="d-flex justify-center align-center px-4"
      >
        <v-img
          src="@/assets/appScreenshot.png"
          alt="Feature 3 Image"
          class="feature-image"
        ></v-img>
      </v-col>
    </v-row>
  </v-container>

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
    background-color: rgb(var(--v-theme-surface-variant)); /* Light grey background */
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

/* Features Section Styles */
.features-container {
  max-width: 1000px;
  margin: 2rem auto; /* Add some spacing above and below */
  padding-left: 16px;
  padding-right: 16px;
}

.feature-text {
  max-width: 60%; /* Adjust as needed */
}

.features-header {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

.feature-item {
  margin-bottom: 1.5rem;
}

.feature-item h3 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.feature-row{
  margin-bottom:5rem;
}

.feature-item p {
  font-size: 1rem;
  color: #757575;
}

/* Features Image */
.feature-image {
  max-width: 80%;
  max-height: 400px;
  height: auto;
  display: block;
  border-radius: 12px;
  border: 2px solid #ddd;
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.3);
}

/* Adjustments for alternating rows */
.flex-row-reverse {
  flex-direction: row-reverse;
}

/* Align-center class */
.align-center {
  display: flex;
  align-items: center;
}

</style>