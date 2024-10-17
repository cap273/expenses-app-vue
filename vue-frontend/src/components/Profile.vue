<template>
    <v-container>
      <v-card>
        <v-card-title>Profile Settings</v-card-title>
        <v-card-text>
          <v-form ref="form" @submit.prevent="submitProfileUpdate">
            <!-- Username Field -->
            <v-text-field
              v-model="newUsername"
              label="New Username"
              :rules="[rules.username]"
              clearable
            ></v-text-field>
  
            <!-- Password Fields -->
            <v-text-field
              v-model="currentPassword"
              :type="showCurrentPassword ? 'text' : 'password'"
              label="Current Password"
              :append-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append="showCurrentPassword = !showCurrentPassword"
              :rules="currentPasswordRules"
              clearable
            ></v-text-field>
  
            <v-text-field
              v-model="newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              label="New Password"
              :append-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append="showNewPassword = !showNewPassword"
              :rules="newPasswordRules"
              clearable
            ></v-text-field>
  
            <v-text-field
              v-model="confirmNewPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              label="Confirm New Password"
              :append-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append="showConfirmPassword = !showConfirmPassword"
              :rules="confirmPasswordRules"
              clearable
            ></v-text-field>
  
            <v-btn
              type="submit"
              color="primary"
              :loading="loading"
              :disabled="loading"
              class="mt-4"
            >
              Update Profile
            </v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-alert
            v-if="responseMessage"
            :type="responseType"
            dismissible
            class="mt-3 w-100"
          >
            {{ responseMessage }}
          </v-alert>
        </v-card-actions>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import { ref, computed } from 'vue';
  import { globalState } from '@/main.js'; // Import global state if needed
  
  export default {
    name: 'Profile',
    setup() {
      const newUsername = ref('');
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
        username: (value) =>
          !value || /^[a-zA-Z0-9_]{3,20}$/.test(value) ||
          'Username must be 3-20 characters and contain only letters, numbers, and underscores.',
      };
  
      // Conditional rules
      const currentPasswordRules = computed(() => {
        const rulesArray = [];
        if (newPassword.value || confirmNewPassword.value) {
          rulesArray.push(rules.required);
        }
        return rulesArray;
      });
  
      const newPasswordRules = computed(() => {
        const rulesArray = [];
        if (currentPassword.value || confirmNewPassword.value) {
          rulesArray.push(rules.minLength);
        }
        return rulesArray;
      });
  
      const confirmPasswordRules = computed(() => {
        const rulesArray = [];
        if (newPassword.value) {
          rulesArray.push(rules.passwordMatch);
        }
        return rulesArray;
      });
  
      const submitProfileUpdate = async () => {
        responseMessage.value = '';
        responseType.value = '';
  
        // Custom validation logic
        let isValid = true;
  
        // Validate form fields
        if (!form.value.validate()) {
          isValid = false;
        }
  
        // Additional validation for password match
        if (newPassword.value && newPassword.value !== confirmNewPassword.value) {
          responseMessage.value = 'New passwords do not match.';
          responseType.value = 'error';
          isValid = false;
        }
  
        // Ensure that at least one field is being updated
        if (!newUsername.value && !newPassword.value && !confirmNewPassword.value) {
          responseMessage.value = 'Please enter a new username or password to update.';
          responseType.value = 'error';
          isValid = false;
        }
  
        if (!isValid) {
          return;
        }
  
        loading.value = true;
  
        try {
          const payload = {
            new_username: newUsername.value || null,
            current_password: currentPassword.value || null,
            new_password: newPassword.value || null,
          };
  
          const response = await fetch('/api/update_profile', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          });
  
          const data = await response.json();
  
          if (data.success) {
            responseMessage.value = data.message || 'Profile updated successfully.';
            responseType.value = 'success';
  
            // Update global state if username changed
            if (data.updated_username) {
              globalState.username = data.updated_username;
            }
  
            // Clear form fields
            newUsername.value = '';
            currentPassword.value = '';
            newPassword.value = '';
            confirmNewPassword.value = '';
            form.value.resetValidation();
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
        newUsername,
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
        currentPasswordRules,
        newPasswordRules,
        confirmPasswordRules,
        submitProfileUpdate,
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
  