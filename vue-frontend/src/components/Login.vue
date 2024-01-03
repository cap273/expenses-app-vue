<template>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-card>
            <v-card-title>Login</v-card-title>
            <v-card-text>
              <v-form>
                <v-text-field
                  v-model="loginData.usernameOrEmail"
                  label="Username or Email"
                  type="text"
                ></v-text-field>
                <v-text-field
                  v-model="loginData.password"
                  label="Password"
                  type="password"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" @click="loginUser">Login</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        loginData: {
          usernameOrEmail: '',
          password: ''
        },
        errorMessage: ''
      };
    },
    methods: {
      loginUser() {
        fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.loginData.usernameOrEmail, // Send as 'username' to match the backend
            password: this.loginData.password
          })
        })
        .then(response => {
          if (!response.ok) throw new Error('Login failed');
          return response.json();
        })
        .then(data => {
          if (data.success) {
            this.$router.push('/'); // Redirect to main page
            this.$emit('update:user', data.username); // Emit event to update user info
          } else {
            this.errorMessage = data.error;
          }
        })
        .catch(error => {
          this.errorMessage = error.message;
        });
      }
    }
  };
  </script>  