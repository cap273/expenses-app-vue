<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6" style="max-width: 500px;" class="mx-auto">
        <v-card>
          <v-card-title>Create Account</v-card-title>
          <v-card-text>
            <v-form ref="form" @submit.prevent="createAccount">

              <v-text-field
                v-model="signupData.username"
                :rules="rules.username"
                label="Username"
                type="text"
                placeholder="Enter your username"
                prepend-inner-icon="mdi-account"
              ></v-text-field>

              <v-text-field
                v-model="signupData.email"
                :rules="rules.email"
                label="Email"
                type="email"
                placeholder="Enter your email"
                prepend-inner-icon="mdi-email-outline"
              ></v-text-field>

              <v-text-field
                v-model="signupData.password"
                :rules="rules.password"
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

      rules: {
        email: [
          v => !!v || 'Email is required',
          v => /.+@.+\..+/.test(v) || 'E-mail must be valid'
        ],
        username: [
          v => !!v || 'Username is required',
          v => v.length >= 3 || 'Username must be more than 3 characters'
        ],
        password: [
          v => !!v || 'Password is required',
          v => v.length >= 8 || 'Password must be 8 characters or more'
        ]
      },
    
      errorMessage: '',
      loading: false, // Add a loading state
      visible: false // Controls the visibility of the password
    };
  },
  methods: {
    createAccount() {
      if (this.$refs.form.validate()) {
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