<template>
    <v-container class="household-settings-div">
      <div class="rounded-box">
        <h2 class="text-h5 mb-6">Household Settings</h2>

        <!-- Loader while fetching data -->
      <v-progress-circular v-if="isLoading" indeterminate color="primary">
      </v-progress-circular>
        
      <!-- Current Scopes -->
      <div class="mb-8">
        <h3 class="text-h6 mb-4">Your Scopes</h3>
        <v-card
          v-for="scope in scopes"
          :key="scope.id"
          class="mb-4 pa-4 scope-card"
          variant="outlined"
        >
          <!-- Invite Member button at the top right -->
          <v-btn
            v-if="scope.type === 'household' && scope.access_type === 'owner'"
            color="primary"
            @click="showInviteModal(scope.id)"
            prepend-icon="mdi-account-plus"
            class="invite-btn"
            small
          >
            Invite Member
          </v-btn>

          <div class="d-flex flex-column">
            <div class="text-h6">{{ scope.name }}</div>
            <div class="text-body-2 text-grey">
              Type: {{ scope.type === 'household' ? 'Household' : 'Personal' }}
            </div>
            <div class="text-body-2 text-grey">
              Access: {{ scope.access_type === 'owner' ? 'Owner' : 'Member' }}
            </div>

            <!-- Display household members -->
            <div v-if="scope.members && scope.members.length > 0">
              <h4 class="text-subtitle-1 mt-4 mb-2">Members</h4>
              <div class="member-chips">
                <v-chip
                  v-for="member in scope.members"
                  :key="member.email"
                  class="ma-2 member-chip"
                  outlined
                  color="primary"
                  large
                >
                  <v-avatar left>{{ member.email[0].toUpperCase() }}</v-avatar>
                  <span class="font-weight-bold">{{ member.email }}</span>
                  <v-icon right size="18px" style="margin-left:10px">
                    {{ member.access_type === 'owner' ? 'mdi-crown' : 'mdi-account' }}
                  </v-icon>
                </v-chip>
              </div>
            </div>
          </div>
        </v-card>
      </div>
  
        <!-- Create New Household -->
        <div class="mb-8">
          <h3 class="text-h6 mb-4">Create New Household</h3>
          <v-form @submit.prevent="createHousehold">
            <v-text-field
              v-model="newHouseholdName"
              label="Household Name"
              placeholder="Enter household name"
              :rules="[v => !!v || 'Household name is required']"
              class="mb-4"
            ></v-text-field>
            <v-btn
              color="primary"
              type="submit"
              :disabled="!newHouseholdName"
              :loading="isCreating"
              prepend-icon="mdi-plus"
            >
              Create Household
            </v-btn>
          </v-form>
        </div>
  
        <!-- Pending Invitations -->
        <div v-if="pendingInvites.length > 0" class="mb-8">
          <h3 class="text-h6 mb-4">Pending Invitations</h3>
          <v-card
            v-for="invite in pendingInvites"
            :key="invite.scope_id"
            class="mb-4 pa-4"
            variant="outlined"
          >
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h6">{{ invite.scope_name }}</div>
                <div class="text-body-2 text-grey">
                  Invited by: {{ invite.inviter_email }}
                </div>
              </div>
              <div class="d-flex gap-2">
                <v-btn
                  color="success"
                  @click="respondToInvite(invite.scope_id, 'accept')"
                  :loading="isResponding === invite.scope_id"
                >
                  Accept
                </v-btn>
                <v-btn
                  color="error"
                  @click="respondToInvite(invite.scope_id, 'reject')"
                  :loading="isResponding === invite.scope_id"
                >
                  Reject
                </v-btn>
              </div>
            </div>
          </v-card>
        </div>
      </div>
  
      <!-- Invite Modal -->
      <v-dialog v-model="showingInviteModal" max-width="500px">
        <v-card>
          <v-card-title>Invite to Household</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="sendInvite">
              <v-text-field
                v-model="inviteEmail"
                label="Email Address"
                type="email"
                :rules="[
                  v => !!v || 'Email is required',
                  v => /.+@.+\..+/.test(v) || 'Email must be valid'
                ]"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="closeInviteModal">Cancel</v-btn>
            <v-btn
              color="primary"
              @click="sendInvite"
              :disabled="!inviteEmail || !/.+@.+\..+/.test(inviteEmail)"
              :loading="isSending"
            >
              Send Invite
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script>
  export default {
    name: 'HouseholdSettings',
    data() {
      return {
        scopes: [],
        pendingInvites: [],
        newHouseholdName: '',
        showingInviteModal: false,
        inviteEmail: '',
        selectedScopeId: null,
        isCreating: false,
        isSending: false,
        isResponding: null,
        isLoading: true, // Add loading state
      }
    },
    mounted() {
      this.fetchScopes()
      this.fetchPendingInvites()
    },
    methods: {
        async fetchScopes() {
            try {
                const response = await fetch('/api/get_scopes')
                const data = await response.json()
                if (data.success) {
                this.scopes = data.scopes;
                // Fetch members for each scope
                for (const scope of this.scopes) {
                        if (scope.type === 'household') {
                            const memberResponse = await fetch(`/api/get_household_members?scopeId=${scope.id}`);
                            const memberData = await memberResponse.json();
                            if (memberData.success) {
                                scope.members = memberData.members;
                            } else {
                                scope.members = [];
                            }
                        }
                    }
                } else {
                console.error('Error fetching scopes:', data.error)
                }
            } catch (error) {
                console.error('Error fetching scopes:', error)
            }
            finally {
                this.isLoading = false;
            }
            },
            async fetchPendingInvites() {
            try {
                const response = await fetch('/api/get_pending_invites')
                const data = await response.json()
                if (data.success) {
                this.pendingInvites = data.invites
                } else {
                console.error('Error fetching pending invites:', data.error)
                }
            } catch (error) {
                console.error('Error fetching pending invites:', error)
            }
            },  
      async createHousehold() {
        if (!this.newHouseholdName) return
        
        this.isCreating = true
        try {
          const response = await fetch('/api/create_household', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: this.newHouseholdName,
            }),
          })
          const data = await response.json()
          if (data.success) {
            this.newHouseholdName = ''
            await this.fetchScopes()
            this.$toast.success('Household created successfully')
          } else {
            this.$toast.error(data.error || 'Failed to create household')
          }
        } catch (error) {
          console.error('Error creating household:', error)
          this.$toast.error('Failed to create household')
        } finally {
          this.isCreating = false
        }
      },
  
      async sendInvite() {
        if (!this.inviteEmail || !/.+@.+\..+/.test(this.inviteEmail)) return
        
        this.isSending = true
        try {
          const response = await fetch('/api/invite_to_household', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: this.inviteEmail,
              scopeId: this.selectedScopeId,
            }),
          })
          const data = await response.json()
          if (data.success) {
            this.closeInviteModal()
            this.$toast.success('Invitation sent successfully')
          } else {
            this.$toast.error(data.error || 'Failed to send invitation')
          }
        } catch (error) {
          console.error('Error sending invitation:', error)
          this.$toast.error('Failed to send invitation')
        } finally {
          this.isSending = false
        }
      },
  
      async respondToInvite(scopeId, response) {
        this.isResponding = scopeId
        try {
          const apiResponse = await fetch('/api/respond_to_invite', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              scopeId,
              response,
            }),
          })
          const data = await apiResponse.json()
          if (data.success) {
            await Promise.all([
              this.fetchScopes(),
              this.fetchPendingInvites(),
            ])
            this.$toast.success(`Invitation ${response}ed successfully`)
          } else {
            this.$toast.error(data.error || `Failed to ${response} invitation`)
          }
        } catch (error) {
          console.error('Error responding to invitation:', error)
          this.$toast.error(`Failed to ${response} invitation`)
        } finally {
          this.isResponding = null
        }
      },
  
      showInviteModal(scopeId) {
      this.selectedScopeId = scopeId
      this.showingInviteModal = true
      this.inviteEmail = ''
        },
        closeInviteModal() {
        this.showingInviteModal = false
        this.selectedScopeId = null
        this.inviteEmail = ''
        },
    },
  }
  </script>
  
  <style scoped>
  .rounded-box {
    background-color: #f5f5f5;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .gap-2 {
    gap: 8px;
  }

  /* Invite button absolute positioning */
.scope-card {
  position: relative;
}

.invite-btn {
  position: absolute;
  top: 10px;
  right: 10px;
}

/* Member chips layout */
.member-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.member-chip {
  padding: 24px 24px; /* Add more padding to make it roomier */
}

.ma-2 {
  margin: 8px;
}

.household-settings-div {
    max-width: 750px;
}
  </style>