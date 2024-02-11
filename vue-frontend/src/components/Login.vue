<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6" style="max-width: 500px;" class="mx-auto">
        <v-card>
          <v-card-title>Login</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="loginUser">
              <v-text-field
                v-model="loginData.usernameOrEmail"
                label="Username or Email"
                type="text"
                placeholder="Enter your email or username"
              ></v-text-field>
              <v-text-field
                v-model="loginData.password"
                label="Password"
                :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
                :type="visible ? 'text' : 'password'"
                placeholder="Enter your password"
                prepend-inner-icon="mdi-lock-outline"
                @click:append-inner="togglePasswordVisibility"
              ></v-text-field>
            </v-form>
            <div class="text-center red--text text-bold">{{ errorMessage }}</div>
            <v-card-actions class="justify-center">
              <v-btn 
                color="primary" 
                type="submit" 
                :loading="loading"
                @click="loginUser"
              >
                Login
              </v-btn>
            </v-card-actions>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { globalState } from '@/main.js';

export default {
  data() {
    return {
      loginData: {
        usernameOrEmail: '',
        password: ''
      },
      errorMessage: '',
      loading: false, // Add a loading state
      visible: false // Controls the visibility of the password
    };
  },
  methods: {
    loginUser() {
      this.loading = true; // Activate loading animation
      fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: this.loginData.usernameOrEmail,
          password: this.loginData.password
        })
      })
      .then(response => {
        this.loading = false; // Deactivate loading animation
        if (!response.ok) throw new Error('Login failed');
        return response.json();
      })
      .then(data => {
        if (data.authenticated) {
          globalState.authenticated = true;
          globalState.username = data.username;
          this.$router.push('/input_expenses'); // Redirect to Input Expenses page
        } else {
          this.errorMessage = data.error || 'Authentication failed';
        }
      })
      .catch(error => {
        this.loading = false; // Deactivate loading animation on error
        this.errorMessage = error.message || 'An error occurred during login';
      });
    },

    // Add a method to toggle password visibility
    togglePasswordVisibility() {
      this.visible = !this.visible;
    },
  }
};
</script>

<style scoped>
.red--text.text-bold {
  color: red;
  font-weight: bold;
  text-align: center;
}
</style>