<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>Create Account</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="createAccount">
              <v-text-field
                v-model="signupData.username"
                label="Username"
                type="text"
              ></v-text-field>
              <v-text-field
                v-model="signupData.email"
                label="Email"
                type="email"
              ></v-text-field>
              <v-text-field
                v-model="signupData.password"
                label="Password"
                type="password"
              ></v-text-field>
            </v-form>
            <div class="text-center red--text text-bold">{{ errorMessage }}</div>
            <v-card-actions class="justify-center">
              <v-btn 
                color="primary" 
                type="submit" 
                :loading="loading"
                @click="createAccount"
              >
                Create Account
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
      signupData: {
        usernameOrEmail: '',
        password: ''
      },
      errorMessage: '',
      loading: false // Add a loading state
    };
  },
  methods: {
    createAccount() {
      this.loading = true; // Activate loading animation
      fetch('/api/create_account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: this.signupData.username,
          email: this.signupData.email,
          password: this.signupData.password
        })
      })
      .then(response => {
        this.loading = false; // Deactivate loading animation
        if (!response.ok) throw new Error('Account creation failed');
        return response.json();
      })
      .then(data => {
        if (!data.success) {
            this.errorMessage = data.error || 'Account creation failed';
        }
        else {
            if (data.authenticated) {
                globalState.authenticated = true;
                globalState.username = data.username;
                this.$router.push('/input_expenses'); // Redirect to Input Expenses page
            } else {
                this.errorMessage = data.error || 'Account creation failed';
            }
        }
      })
      .catch(error => {
        this.loading = false; // Deactivate loading animation on error
        this.errorMessage = error.message || 'An error occurred during account creation';
      });
    }
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