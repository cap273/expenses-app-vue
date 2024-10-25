<template>
  <v-container>
    <v-card>
      <v-card-title>Profile Settings</v-card-title>
        <v-card-text>
          <!-- Display existing email -->
          <v-text-field
            v-model="email"
            label="Email"
            readonly
          ></v-text-field>

          <!-- Username Field with Save Button -->
          <v-row>
            <v-col>
              <v-text-field
                v-model="newUsername"
                label="Username"
                :rules="[rules.username]"
                clearable
              ></v-text-field>
            </v-col>
            <v-col cols="auto">
              <v-btn
                color="primary"
                @click="updateUsername"
                :loading="loadingUsername"
                :disabled="loadingUsername || !newUsername"
              >
                Save
              </v-btn>
            </v-col>
          </v-row>

          <!-- Password Update Section -->
          <v-divider class="my-4"></v-divider>
          <v-card-title>Update Password</v-card-title>
            <v-form ref="form" @submit.prevent="updatePassword">
              <!-- Current Password -->
              <v-text-field
                v-model="currentPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                label="Current Password"
                :append-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showCurrentPassword = !showCurrentPassword"
                :rules="currentPasswordRules"
                clearable
              ></v-text-field>

              <!-- New Password -->
              <v-text-field
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                label="New Password"
                :append-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showNewPassword = !showNewPassword"
                :rules="newPasswordRules"
                clearable
              ></v-text-field>

              <!-- Confirm New Password -->
              <v-text-field
                v-model="confirmNewPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                label="Confirm New Password"
                :append-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showConfirmPassword = !showConfirmPassword"
                :rules="confirmPasswordRules"
                clearable
              ></v-text-field>

              <!-- Update Password Button -->
              <v-btn
                type="submit"
                color="primary"
                :loading="loadingPassword"
                :disabled="loadingPassword || !newPassword || !currentPassword || !confirmNewPassword"
                class="mt-4"
              >
                Update Password
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
import { ref, computed, onMounted } from 'vue';
import { globalState } from '@/main.js';

export default {
  name: 'Profile',
  setup() {
    // Initialize with globalState values
    const email = ref('');
    const newUsername = ref('');
    const currentPassword = ref('');
    const newPassword = ref('');
    const confirmNewPassword = ref('');
    const showCurrentPassword = ref(false);
    const showNewPassword = ref(false);
    const showConfirmPassword = ref(false);
    const loadingUsername = ref(false);
    const loadingPassword = ref(false);
    const responseMessage = ref('');
    const responseType = ref('');

    // Initialize user data from globalState
    onMounted(() => {
      // Fetch fresh data when component mounts
      fetch('/api/auth/status')
        .then(response => response.json())
        .then(data => {
          if (data.authenticated) {
            email.value = data.email || 'N/A';
            newUsername.value = data.username || '';
          }
        })
        .catch(error => {
          console.error('Error fetching user data:', error);
        });
    });

    const rules = {
      username: (value) =>
        !value || /^[a-zA-Z0-9_]{3,20}$/.test(value) ||
        'Username must be 3-20 characters and contain only letters, numbers, and underscores.',
      minLength: (value) => value.length >= 8 || 'Password must be at least 8 characters.',
      passwordMatch: (value) =>
        value === newPassword.value || 'Passwords do not match.',
    };

    // Define computed properties
    const currentPasswordRules = computed(() => {
      if (newPassword.value || confirmNewPassword.value) {
        return [rules.minLength];
      }
      return [];
    });

    const newPasswordRules = computed(() => {
      if (currentPassword.value || confirmNewPassword.value) {
        return [rules.minLength];
      }
      return [];
    });

    const confirmPasswordRules = computed(() => {
      if (newPassword.value) {
        return [rules.passwordMatch];
      }
      return [];
    });

    const updateUsername = async () => {
      loadingUsername.value = true;
      responseMessage.value = '';

      try {
        const payload = {
          new_username: newUsername.value,
        };

        const response = await fetch('/api/update_profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.success) {
          responseMessage.value = 'Username updated successfully.';
          responseType.value = 'success';
          globalState.username = newUsername.value;
          globalState.display_name = newUsername.value;
        } else {
          responseMessage.value = data.error || 'Failed to update username.';
          responseType.value = 'error';
        }
      } catch (error) {
        console.error('Error updating username:', error);
        responseMessage.value = 'An error occurred. Please try again.';
        responseType.value = 'error';
      } finally {
        loadingUsername.value = false;
      }
    };

    const updatePassword = async () => {
      loadingPassword.value = true;
      responseMessage.value = '';

      try {
        const payload = {
          current_password: currentPassword.value,
          new_password: newPassword.value,
        };

        const response = await fetch('/api/change_password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.success) {
          responseMessage.value = 'Password updated successfully.';
          responseType.value = 'success';
          currentPassword.value = '';
          newPassword.value = '';
          confirmNewPassword.value = '';
        } else {
          responseMessage.value = data.error || 'Failed to update password.';
          responseType.value = 'error';
        }
      } catch (error) {
        console.error('Error updating password:', error);
        responseMessage.value = 'An error occurred. Please try again.';
        responseType.value = 'error';
      } finally {
        loadingPassword.value = false;
      }
    };

    // Make sure to return all refs and methods
    return {
      email,
      newUsername,
      currentPassword,
      newPassword,
      confirmNewPassword,
      showCurrentPassword,
      showNewPassword,
      showConfirmPassword,
      loadingUsername,
      loadingPassword,
      responseMessage,
      responseType,
      rules,
      currentPasswordRules,
      newPasswordRules,
      confirmPasswordRules,
      updateUsername,
      updatePassword,
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