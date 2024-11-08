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
                      <div v-else class="d-flex gap-4">
                        <v-btn
                          color="primary"
                          @click="showHouseholdForm = true"
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
                    <div class="d-flex gap-4">
                    <v-btn
                        color="primary"
                        @click="openPlaidLink"
                        :loading="plaidLoading"
                    >
                        Connect Bank Account
                    </v-btn>
                    <v-btn
                        variant="outlined"
                        @click="currentStep++"
                    >
                        Enter Manually
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
                        <PlaidDashboard />
                    </v-card-text>
                    </v-card>
                </v-dialog>
                </v-window-item>

              <!-- Step 4: Theme Selection -->
              <v-window-item :value="4">
                <div>
                  <h2 class="text-h5 mb-4">Appearance</h2>
                  <p class="text-body-1 mb-6">
                    Choose your preferred theme:
                  </p>
                  <v-row>
                    <v-col cols="6">
                      <v-card
                        @click="selectTheme('light')"
                        :class="{ 'border-primary': selectedTheme === 'light' }"
                        class="pa-4 cursor-pointer"
                        elevation="2"
                      >
                        <div class="d-flex align-center justify-center">
                          <v-icon size="32" class="mr-2">mdi-white-balance-sunny</v-icon>
                          <span class="text-body-1">Light Mode</span>
                        </div>
                      </v-card>
                    </v-col>
                    <v-col cols="6">
                      <v-card
                      @click="selectTheme('dark')"
                        :class="{
                        'border-primary': selectedTheme === 'dark',
                        'bg-dark': isDarkTheme,
                        'pa-4': true,
                        'cursor-pointer': true
                        }"
                        elevation="2"
                      >
                        <div class="d-flex align-center justify-center">
                          <v-icon size="32" class="mr-2">mdi-moon-waning-crescent</v-icon>
                          <span class="text-body-1">Dark Mode</span>
                        </div>
                      </v-card>
                    </v-col>
                  </v-row>

                  <!-- Preview/Confirm Theme Button -->
                  <div class="text-center mt-6">
                    <v-btn
                      color="primary"
                      @click="confirmTheme"
                      class="mt-6"
                    >
                      Confirm {{ selectedTheme }} theme
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
                <v-btn
                  v-if="!showHouseholdForm"
                  color="primary"
                  @click="currentStep++"
                >
                  Next
                </v-btn>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue';
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
      const selectedTheme = ref(null);
      const currentTheme = ref(theme.global.current.value.dark ? 'dark' : 'light');

  
      const progress = computed(() => (currentStep.value / totalSteps) * 100);
      const isDarkTheme = computed(() => theme.global.current.value.dark);
  
    // Plaid Link integration
    const openPlaidLink = () => {
      showPlaidDialog.value = true;
    };

    // Theme selection
    const selectTheme = (mode) => {
      selectedTheme.value = mode;
      // Preview the theme
      theme.global.name.value = mode;
    };

    const confirmTheme = () => {
      currentTheme.value = selectedTheme.value;
      currentStep.value++;
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
          if (data.success && partnerEmail.value) {
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
          currentStep.value++;
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
        createHousehold,
        openPlaidLink,
        showPlaidDialog,
        selectTheme,
        confirmTheme,
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
  </style>