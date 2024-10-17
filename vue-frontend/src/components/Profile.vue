<template>
    <v-container>
      <v-card>
        <v-card-title>Change Password</v-card-title>
        <v-card-text>
          <v-form ref="form" @submit.prevent="submitPasswordChange">
            <v-text-field
              v-model="currentPassword"
              :type="showCurrentPassword ? 'text' : 'password'"
              label="Current Password"
              :append-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append="showCurrentPassword = !showCurrentPassword"
              :rules="[rules.required]"
            ></v-text-field>
  
            <v-text-field
              v-model="newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              label="New Password"
              :append-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append="showNewPassword = !showNewPassword"
              :rules="[rules.required, rules.minLength]"
            ></v-text-field>
  
            <v-text-field
              v-model="confirmNewPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              label="Confirm New Password"
              :append-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append="showConfirmPassword = !showConfirmPassword"
              :rules="[rules.required, rules.passwordMatch]"
            ></v-text-field>
  
            <v-btn
              type="submit"
              color="primary"
              :loading="loading"
              :disabled="loading"
            >
              Change Password
            </v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-alert
            v-if="responseMessage"
            :type="responseType"
            dismissible
            class="mt-3"
          >
            {{ responseMessage }}
          </v-alert>
        </v-card-actions>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import { ref } from 'vue';
  
  export default {
    name: 'Profile',
    setup() {
      const currentPassword = ref('');
      const newPassword = ref('');
      const confirmNewPassword = ref('');
      const showCurrentPassword = ref(false);
      const showNewPassword = ref(false);
      const showConfirmPassword = ref(false);
      const loading = ref(false);
      const responseMessage = ref('');
      const responseType = ref(''); // 'success' or 'error'
  
      const rules = {
        required: (value) => !!value || 'Required.',
        minLength: (value) =>
          value.length >= 8 || 'Password must be at least 8 characters.',
        passwordMatch: (value) =>
          value === newPassword.value || 'Passwords do not match.',
      };
  
      const submitPasswordChange = async () => {
        if (!form.value.validate()) {
          return;
        }
  
        loading.value = true;
        responseMessage.value = '';
        responseType.value = '';
  
        try {
          const response = await fetch('/api/change_password', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              current_password: currentPassword.value,
              new_password: newPassword.value,
            }),
          });
  
          const data = await response.json();
  
          if (data.success) {
            responseMessage.value = 'Password changed successfully.';
            responseType.value = 'success';
            currentPassword.value = '';
            newPassword.value = '';
            confirmNewPassword.value = '';
          } else {
            responseMessage.value = data.error || 'An error occurred.';
            responseType.value = 'error';
          }
        } catch (error) {
          responseMessage.value = 'An error occurred. Please try again.';
          responseType.value = 'error';
        } finally {
          loading.value = false;
        }
      };
  
      const form = ref(null);
  
      return {
        currentPassword,
        newPassword,
        confirmNewPassword,
        showCurrentPassword,
        showNewPassword,
        showConfirmPassword,
        loading,
        responseMessage,
        responseType,
        rules,
        submitPasswordChange,
        form,
      };
    },
  };
  </script>
  
  <style scoped>
  .v-card {
    max-width: 500px;
    margin: auto;
  }
  </style>
  