<template>
  <div class="onboarding-container">
    <v-container class="py-8">
      <v-row justify="center">
        <v-col cols="12" sm="10" md="8" lg="6">
          <v-card class="pa-6">
            <!-- Progress Bar -->
            <v-progress-linear
              :model-value="progress"
              color="primary"
              height="8"
              rounded
              class="mb-4"
            ></v-progress-linear>

            <!-- Step 1: Welcome -->
            <v-window v-model="currentStep">
              <v-window-item :value="1">
                <div class="text-center">
                  <h2 class="text-h4 mb-6">Welcome to ExpenseTracker!</h2>
                  <p class="text-body-1 mb-6">
                    Let's walk through a few steps to set up your account and get you started.
                  </p>
                  <v-btn
                    color="primary"
                    @click="currentStep++"
                    size="large"
                  >
                    Let's Begin
                  </v-btn>
                </div>
              </v-window-item>

              <!-- Step 2: Household Setup -->
              <v-window-item :value="2">
                <div>
                  <h2 class="text-h5 mb-4">Expense Organization</h2>
                  <p class="text-body-1 mb-6">
                    By default, all expenses go into your personal scope. Would you like to create a
                    household for shared expenses?
                  </p>
                  
                  <!-- Success message after household creation -->
                  <v-alert
                    v-if="householdCreated"
                    type="success"
                    variant="tonal"
                    class="mb-4"
                    dismissible
                  >
                    Successfully created household "{{ createdHouseholdName }}"
                  </v-alert>
                  
                  <v-expand-transition>
                    <div v-if="showHouseholdForm">
                      <v-form @submit.prevent="createHousehold">
                        <v-text-field
                          v-model="householdName"
                          label="Household Name"
                          required
                          class="mb-4"
                        ></v-text-field>
                        <v-text-field
                          v-model="partnerEmail"
                          label="Partner's Email (optional)"
                          type="email"
                          class="mb-4"
                        ></v-text-field>
                        <div class="d-flex gap-4">
                          <v-btn
                            color="primary"
                            :loading="loading"
                            type="submit"
                            class="me-3"
                          >
                            Create Household
                          </v-btn>
                          <v-btn
                            variant="outlined"
                            @click="showHouseholdForm = false"
                          >
                            Cancel
                          </v-btn>
                        </div>
                      </v-form>
                    </div>
                    <div v-else-if="householdCreated" class="d-flex flex-column flex-sm-row gap-4">
                      <v-btn
                        color="primary"
                        @click="resetHouseholdForm"
                        class="me-3 mb-2 mb-sm-0"
                      >
                        Create Another Household
                      </v-btn>
                      <v-btn
                        variant="outlined"
                        @click="currentStep++"
                      >
                        Next
                      </v-btn>
                    </div>
                    <div v-else class="d-flex flex-column flex-sm-row gap-4">
                      <v-btn
                        color="primary"
                        @click="showHouseholdForm = true"
                        class="me-3 mb-2 mb-sm-0"
                      >
                        Create Household
                      </v-btn>
                      <v-btn
                        variant="outlined"
                        @click="currentStep++"
                      >
                        Just Personal
                      </v-btn>
                    </div>
                  </v-expand-transition>
                </div>
              </v-window-item>

              <!-- Step 3: Expense Import -->
              <v-window-item :value="3">
                <div>
                  <h2 class="text-h5 mb-4">Expense Import</h2>
                  <p class="text-body-1 mb-6">
                    How would you like to track your expenses?
                  </p>
                  
                  <!-- Success message after bank connection -->
                  <v-alert
                    v-if="bankConnected"
                    type="success"
                    variant="tonal"
                    class="mb-4"
                    dismissible
                  >
                    Successfully connected to {{ connectedBankName }}
                    <div class="mt-1 text-caption">
                      All transactions will be imported to {{ connectedScopeName }}
                    </div>
                  </v-alert>
                  
                  <div class="d-flex flex-column flex-sm-row gap-4">
                    <v-btn
                      color="primary"
                      @click="openPlaidLink"
                      :loading="plaidLoading"
                      class="me-3 mb-2 mb-sm-0"
                    >
                      {{ bankConnected ? 'Connect Another Bank' : 'Connect Bank Account' }}
                    </v-btn>
                    <v-btn
                      variant="outlined"
                      @click="currentStep++"
                    >
                      {{ bankConnected ? 'Next' : 'Enter Manually' }}
                    </v-btn>
                  </div>
                </div>

                <!-- Move dialog outside the d-flex -->
                <v-dialog v-model="showPlaidDialog" width="800">
                  <v-card>
                    <v-card-title class="text-h5">
                      Connect Your Bank Account
                      <v-spacer></v-spacer>
                      <v-btn icon @click="showPlaidDialog = false">
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </v-card-title>
                    <v-card-text>
                      <PlaidDashboard @connection-success="onPlaidConnectionSuccess" />
                    </v-card-text>
                  </v-card>
                </v-dialog>
              </v-window-item>

              <!-- Step 4: Theme Selection -->
              <v-window-item :value="4">
                <div>
                  <h2 class="text-h5 mb-4">Appearance</h2>
                  <p class="text-body-1 mb-3">
                    Choose your preferred theme:
                  </p>
                  <p class="text-body-2 text-medium-emphasis mb-5">
                    You can always change this later in your profile settings.
                  </p>
                  <v-row class="mb-6">
                    <v-col cols="12" sm="6" class="mb-4 mb-sm-0">
                      <v-card
                        @click="selectTheme('light')"
                        :class="{ 'border-primary': selectedTheme === 'light' }"
                        class="pa-4 cursor-pointer theme-card"
                        elevation="2"
                      >
                        <div class="d-flex align-center justify-center">
                          <v-icon size="32" class="mr-2">mdi-white-balance-sunny</v-icon>
                          <span class="text-body-1">Light Mode</span>
                        </div>
                        <div v-if="selectedTheme === 'light'" class="mt-2 text-center">
                          <v-chip color="primary" size="small">Current Selection</v-chip>
                        </div>
                      </v-card>
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-card
                        @click="selectTheme('dark')"
                        :class="{
                          'border-primary': selectedTheme === 'dark',
                          'bg-dark': isDarkTheme,
                          'pa-4': true,
                          'cursor-pointer': true,
                          'theme-card': true
                        }"
                        elevation="2"
                      >
                        <div class="d-flex align-center justify-center">
                          <v-icon size="32" class="mr-2">mdi-moon-waning-crescent</v-icon>
                          <span class="text-body-1">Dark Mode</span>
                        </div>
                        <div v-if="selectedTheme === 'dark'" class="mt-2 text-center">
                          <v-chip color="primary" size="small">Current Selection</v-chip>
                        </div>
                      </v-card>
                    </v-col>
                  </v-row>
                  <div class="text-center">
                    <v-btn
                      color="primary"
                      size="large"
                      @click="confirmThemeAndContinue"
                    >
                      Confirm {{ selectedTheme === 'light' ? 'Light' : 'Dark' }} Theme
                    </v-btn>
                  </div>
                </div>
              </v-window-item>

              <!-- Step 5: Completion -->
              <v-window-item :value="5">
                <div class="text-center">
                  <h2 class="text-h4 mb-6">You're All Set!</h2>
                  <p class="text-body-1 mb-6">
                    Let's take a look at your new expense dashboard.
                  </p>
                  <v-btn
                    color="primary"
                    size="large"
                    @click="completeOnboarding"
                  >
                    Go to Dashboard
                  </v-btn>
                </div>
              </v-window-item>
            </v-window>

            <!-- Navigation Buttons -->
            <div class="d-flex justify-space-between mt-6" v-if="currentStep > 1 && currentStep < 5">
              <v-btn
                variant="text"
                @click="currentStep--"
              >
                Back
              </v-btn>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useTheme } from 'vuetify';
import { useRouter } from 'vue-router';
import { usePlaid } from '@/composables/usePlaid';
import PlaidDashboard from '@/views/PlaidDashboard.vue';

export default {
  name: 'OnboardingFlow',
  components: {
    PlaidDashboard,
  },
  
  setup() {
    const router = useRouter();
    const theme = useTheme();
    const { state: plaidState, generateToken } = usePlaid();
    const showPlaidDialog = ref(false);
    const currentStep = ref(1);
    const totalSteps = 5;
    const householdName = ref('');
    const partnerEmail = ref('');
    const showHouseholdForm = ref(false);
    const loading = ref(false);
    const plaidLoading = ref(false);
    
    // New properties for the updated flow
    const householdCreated = ref(false);
    const createdHouseholdName = ref('');
    const bankConnected = ref(false);
    const connectedBankName = ref('');
    const connectedScopeName = ref('');
    
    const progress = computed(() => (currentStep.value / totalSteps) * 100);
    const isDarkTheme = computed(() => theme.global.current.value.dark);
    
    // Set initial theme selection based on current theme
    const selectedTheme = ref(isDarkTheme.value ? 'dark' : 'light');
    const currentTheme = ref(theme.global.name.value);

    // Plaid Link integration
    const openPlaidLink = () => {
      plaidLoading.value = true;
      showPlaidDialog.value = true;
    };

    // Reset household form for creating another household
    const resetHouseholdForm = () => {
      householdName.value = '';
      partnerEmail.value = '';
      showHouseholdForm.value = true;
    };

    // Theme selection
    const selectTheme = (mode) => {
      selectedTheme.value = mode;
      // Preview the theme
      theme.global.name.value = mode;
    };

    // Combined confirm and continue function
    const confirmThemeAndContinue = () => {
      currentTheme.value = selectedTheme.value;
      currentStep.value++;
    };

    // Handle Plaid connection success
    const onPlaidConnectionSuccess = (data) => {
      console.log("Plaid connection success received:", data);
      bankConnected.value = true;
      connectedBankName.value = data.institution_name || 'your bank';
      plaidLoading.value = false;
      
      // Get scope name from the scope ID
      fetchScopeName(data.scope_id);
      
      showPlaidDialog.value = false;
    };
    
    // Fetch scope name based on scope ID
    const fetchScopeName = async (scopeId) => {
      try {
        const response = await fetch('/api/get_scopes');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.scopes) {
            const scope = data.scopes.find(s => s.id === scopeId);
            if (scope) {
              connectedScopeName.value = scope.name;
            } else {
              connectedScopeName.value = 'selected scope';
            }
          }
        }
      } catch (error) {
        console.error('Error fetching scope name:', error);
        connectedScopeName.value = 'selected scope';
      }
    };

    const createHousehold = async () => {
      if (!householdName.value) return;
      
      loading.value = true;
      try {
        const response = await fetch('/api/create_household', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: householdName.value,
          }),
        });

        const data = await response.json();
        if (data.success) {
          // Update state to show success
          householdCreated.value = true;
          createdHouseholdName.value = householdName.value;
          showHouseholdForm.value = false;
          
          // Send invite if email provided
          if (partnerEmail.value) {
            await fetch('/api/invite_to_household', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                email: partnerEmail.value,
                scopeId: data.household.id,
              }),
            });
          }
        }
      } catch (error) {
        console.error('Error creating household:', error);
      } finally {
        loading.value = false;
      }
    };

    const completeOnboarding = async () => {
      try {
        await fetch('/api/complete_onboarding', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        router.push('/overview');
      } catch (error) {
        console.error('Error completing onboarding:', error);
      }
    };

    onMounted(() => {
      // Load Plaid Link script if not already loaded
      if (typeof window !== 'undefined' && !window.Plaid) {
        const script = document.createElement('script');
        script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
        document.head.appendChild(script);
      }
    });

    return {
      currentStep,
      progress,
      householdName,
      partnerEmail,
      showHouseholdForm,
      loading,
      plaidLoading,
      isDarkTheme,
      selectedTheme,
      currentTheme,
      householdCreated,
      createdHouseholdName,
      bankConnected,
      connectedBankName,
      connectedScopeName,
      createHousehold,
      resetHouseholdForm,
      openPlaidLink,
      showPlaidDialog,
      selectTheme,
      confirmThemeAndContinue,
      onPlaidConnectionSuccess,
      completeOnboarding,
    };
  },
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.border-primary {
  border: 2px solid rgb(var(--v-theme-primary));
}

.gap-4 {
  gap: 1rem;
}

.onboarding-container {
  min-height: 100%;
  width: 100%;
  padding: 2rem 0;
}

.theme-card {
  height: 100%;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.3s ease;
}

.theme-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

/* Add margin to separate buttons */
.me-3 {
  margin-right: 12px;
}

.mb-2 {
  margin-bottom: 8px;
}

/* For small screens and up, remove bottom margin for buttons in a row */
@media (min-width: 600px) {
  .mb-sm-0 {
    margin-bottom: 0 !important;
  }
}
</style>