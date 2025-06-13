<template>
  <v-card class="pa-3 hover-elevate h-100">
    <div class="d-flex align-center justify-space-between mb-2">
      <h3 class="text-h6 mb-0">Monthly Category Targets</h3>
      <v-menu location="bottom end">
        <template v-slot:activator="{ props }">
          <v-btn icon variant="text" v-bind="props" size="small">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="showTargetEditor = true; openTargetEditor()">
            <v-list-item-title>Edit Targets</v-list-item-title>
          </v-list-item>
          <v-list-item @click="generateTargetsFromAverages">
            <v-list-item-title>Generate from Averages</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
    <v-divider class="mb-3"></v-divider>
    
    <div v-if="loading" class="d-flex justify-center my-4">
      <v-progress-circular indeterminate size="24" />
    </div>
    
    <div v-else-if="progressData.length > 0" class="targets-container">
      <div 
        v-for="(progress, idx) in progressData" 
        :key="progress.target_id || 'everything-else'"
        class="target-item mb-3"
        :class="{ 'everything-else-item': progress.is_everything_else }"
      >
        <div class="d-flex align-center justify-space-between mb-1">
          <span class="target-category">
            <v-icon v-if="progress.is_everything_else" size="small" class="mr-1">mdi-dots-horizontal</v-icon>
            {{ progress.category }}
          </span>
          <span v-if="!progress.is_everything_else || progress.monthly_target > 0" class="target-amount">
            {{ formatCurrency(progress.monthly_target) }}
          </span>
          <span v-else class="target-amount text-medium-emphasis">
            No target set
          </span>
        </div>
        
        <div class="progress-container">
          <v-progress-linear
            v-if="!progress.is_everything_else || progress.monthly_target > 0"
            :model-value="Math.min(progress.progress_percentage, 100)"
            :color="getProgressColor(progress.progress_percentage, progress.is_over_budget)"
            height="8"
            rounded
            class="mb-1"
          />
          <div v-else class="everything-else-bar mb-1"></div>
          
          <div class="d-flex align-center justify-space-between">
            <span class="progress-text">
              {{ formatCurrency(progress.current_spent) }} spent
              <span v-if="progress.is_over_budget" class="text-error">
                ({{ formatCurrency(Math.abs(progress.remaining)) }} over)
              </span>
              <span v-else-if="!progress.is_everything_else || progress.monthly_target > 0" class="text-medium-emphasis">
                ({{ formatCurrency(progress.remaining) }} left)
              </span>
              <span v-else class="text-medium-emphasis">
                (uncategorized spending)
              </span>
            </span>
            <span v-if="!progress.is_everything_else || progress.monthly_target > 0" 
                  class="progress-percentage" 
                  :class="getProgressTextClass(progress.is_over_budget)">
              {{ Math.round(progress.progress_percentage) }}%
            </span>
            <v-btn v-else
                   size="x-small" 
                   variant="outlined" 
                   color="primary"
                   @click="addEverythingElseToTargets(progress)">
              <v-icon size="small">mdi-target</v-icon>
              Set Target
            </v-btn>
          </div>
        </div>
      </div>
      
      <div class="summary-info mt-4 pt-3" style="border-top: 1px solid rgba(var(--v-theme-on-surface), 0.1);">
        <div class="text-caption text-center">
          <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
          Progress for {{ currentMonth }}
        </div>
      </div>
    </div>
    
    <div v-else class="text-center my-4">
      <div class="text-subtitle-2 mb-2">No category targets set</div>
      <v-btn 
        color="primary" 
        variant="outlined" 
        size="small"
        @click="generateTargetsFromAverages"
      >
        <v-icon left size="small">mdi-target</v-icon>
        Generate Targets
      </v-btn>
    </div>

    <!-- Target Editor Dialog -->
    <v-dialog v-model="showTargetEditor" max-width="600px" scrollable>
      <v-card>
        <v-card-title class="text-h6">
          Edit Monthly Category Targets
        </v-card-title>
        
        <v-card-text>
          <div v-if="loadingAverages" class="d-flex justify-center my-4">
            <v-progress-circular indeterminate size="32" />
          </div>
          
          <div v-else>
            <div class="mb-4">
              <v-btn 
                color="primary" 
                variant="outlined" 
                size="small"
                @click="addCustomTarget"
                class="mr-2"
              >
                <v-icon left size="small">mdi-plus</v-icon>
                Add Custom Target
              </v-btn>
              <v-btn 
                color="secondary" 
                variant="outlined" 
                size="small"
                @click="loadAveragesAsTargets"
              >
                <v-icon left size="small">mdi-chart-line</v-icon>
                Load from 12-Month Averages
              </v-btn>
            </div>

            <div v-for="(target, index) in editableTargets" :key="index" class="target-edit-item mb-3">
              <v-row>
                <v-col cols="6">
                  <v-select
                    v-model="target.category"
                    :items="availableCategories"
                    label="Category"
                    dense
                    variant="outlined"
                    hide-details
                  />
                </v-col>
                <v-col cols="4">
                  <v-text-field
                    v-model.number="target.monthly_target"
                    label="Monthly Target"
                    type="number"
                    step="0.01"
                    dense
                    variant="outlined"
                    hide-details
                    prefix="$"
                  />
                </v-col>
                <v-col cols="2" class="d-flex align-center">
                  <v-btn 
                    icon 
                    variant="text" 
                    size="small"
                    @click="removeTarget(index)"
                    color="error"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </div>

            <div v-if="averages.length > 0" class="mt-4">
              <v-divider class="mb-3" />
              <div class="text-subtitle-2 mb-2">
                Category Averages 
                <span v-if="averages[0]?.active_months" class="text-caption text-medium-emphasis">
                  ({{ averages[0].active_months }} active months)
                </span>
              </div>
              <div class="averages-list">
                <div 
                  v-for="avg in averages.slice(0, 8)" 
                  :key="avg.category"
                  class="average-item d-flex justify-space-between py-1"
                >
                  <span class="text-body-2">{{ avg.category }}</span>
                  <span class="text-body-2 font-weight-medium">{{ formatCurrency(avg.monthly_average) }}</span>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn 
            color="grey" 
            variant="text" 
            @click="showTargetEditor = false"
          >
            Cancel
          </v-btn>
          <v-btn 
            color="primary" 
            variant="elevated"
            @click="saveTargets"
            :loading="saving"
          >
            Save Targets
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { formatCurrency } from '@/utils/formatUtils'

export default {
  name: 'AverageExpenses',
  props: {
    selectedScopes: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const loading = ref(true)
    const loadingAverages = ref(false)
    const saving = ref(false)
    const showTargetEditor = ref(false)
    const progressData = ref([])
    const averages = ref([])
    const editableTargets = ref([])
    const currentMonth = ref('')
    const availableCategories = ref([])

    onMounted(() => {
      fetchProgressData()
    })

    // Watch for changes in selected scopes and refresh data
    watch(() => props.selectedScopes, () => {
      if (props.selectedScopes && props.selectedScopes.length > 0) {
        fetchProgressData()
      }
    }, { deep: true })

    const fetchProgressData = async () => {
      loading.value = true
      try {
        const response = await fetch('/api/get_category_progress')
        const data = await response.json()
        if (data.success) {
          progressData.value = data.progress
          currentMonth.value = data.month
        }
      } catch (error) {
        console.error('Error fetching progress data:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchAverages = async () => {
      loadingAverages.value = true
      try {
        const response = await fetch('/api/get_category_averages')
        const data = await response.json()
        if (data.success) {
          averages.value = data.averages
        }
      } catch (error) {
        console.error('Error fetching averages:', error)
      } finally {
        loadingAverages.value = false
      }
    }

    const fetchAvailableCategories = async () => {
      try {
        const response = await fetch('/api/get_available_categories')
        const data = await response.json()
        if (data.success) {
          availableCategories.value = data.categories
        }
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const generateTargetsFromAverages = async () => {
      await fetchAverages()
      if (averages.value.length > 0) {
        // Use top 6-8 categories from averages
        const topCategories = averages.value.slice(0, 8)
        const targets = topCategories.map(avg => ({
          category: avg.category,
          monthly_target: Math.round(avg.monthly_average),
          scope_id: props.selectedScopes[0] || 1 // Default to first scope
        }))
        
        try {
          const response = await fetch('/api/save_category_targets', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ targets })
          })
          
          const data = await response.json()
          if (data.success) {
            await fetchProgressData() // Refresh the display
          }
        } catch (error) {
          console.error('Error saving targets:', error)
        }
      }
    }

    const loadAveragesAsTargets = () => {
      if (averages.value.length > 0) {
        // Clear existing targets first
        editableTargets.value = []
        
        // Load top 6-8 categories from averages
        editableTargets.value = averages.value.slice(0, 8).map(avg => ({
          category: avg.category,
          monthly_target: Math.round(avg.monthly_average),
          scope_id: props.selectedScopes[0] || 1
        }))
      }
    }

    const addCustomTarget = () => {
      editableTargets.value.push({
        category: '',
        monthly_target: 0,
        scope_id: props.selectedScopes[0] || 1
      })
    }

    const removeTarget = (index) => {
      editableTargets.value.splice(index, 1)
    }

    const saveTargets = async () => {
      saving.value = true
      try {
        const validTargets = editableTargets.value.filter(
          t => t.category && t.monthly_target > 0
        )
        
        const response = await fetch('/api/save_category_targets', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ targets: validTargets })
        })
        
        const data = await response.json()
        if (data.success) {
          showTargetEditor.value = false
          await fetchProgressData() // Refresh the display
        }
      } catch (error) {
        console.error('Error saving targets:', error)
      } finally {
        saving.value = false
      }
    }

    // Open editor and load current targets
    const openTargetEditor = async () => {
      await Promise.all([fetchAverages(), fetchAvailableCategories()])
      
      // Load existing targets
      try {
        const response = await fetch('/api/get_category_targets')
        const data = await response.json()
        if (data.success) {
          editableTargets.value = data.targets.map(t => ({
            category: t.category,
            monthly_target: t.monthly_target,
            scope_id: t.scope_id
          }))
        }
      } catch (error) {
        console.error('Error fetching targets:', error)
      }
    }

    const getProgressColor = (percentage, isOverBudget) => {
      if (isOverBudget) return 'error'
      if (percentage >= 90) return 'warning'
      if (percentage >= 75) return 'orange'
      return 'success'
    }

    const getProgressTextClass = (isOverBudget) => {
      return isOverBudget ? 'text-error font-weight-bold' : 'text-medium-emphasis'
    }

    const addEverythingElseToTargets = (everythingElseData) => {
      // Open the target editor and pre-populate with a target for "Everything Else"
      showTargetEditor.value = true
      openTargetEditor().then(() => {
        // Check if "Everything Else" target already exists
        const existingIndex = editableTargets.value.findIndex(t => t.category === 'Everything Else')
        
        if (existingIndex >= 0) {
          // Update existing target
          editableTargets.value[existingIndex].monthly_target = Math.round(everythingElseData.current_spent)
        } else {
          // Add new "Everything Else" target with the current spending as the target
          editableTargets.value.push({
            category: 'Everything Else',
            monthly_target: Math.round(everythingElseData.current_spent),
            scope_id: props.selectedScopes[0] || 1
          })
        }
      })
    }

    return {
      loading,
      loadingAverages,
      saving,
      showTargetEditor,
      progressData,
      averages,
      editableTargets,
      currentMonth,
      availableCategories,
      fetchProgressData,
      generateTargetsFromAverages,
      loadAveragesAsTargets,
      addCustomTarget,
      removeTarget,
      saveTargets,
      openTargetEditor,
      addEverythingElseToTargets,
      getProgressColor,
      getProgressTextClass,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.targets-container {
  max-height: 400px;
  overflow-y: auto;
}

.target-item {
  padding: 12px;
  border-radius: 8px;
  background-color: rgba(var(--v-theme-surface-variant), 0.3);
  transition: background-color 0.2s ease;
}

.target-item:hover {
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
}

.everything-else-item {
  border: 1px dashed rgba(var(--v-theme-on-surface), 0.2);
  background-color: rgba(var(--v-theme-surface-variant), 0.1);
}

.everything-else-bar {
  height: 8px;
  background: linear-gradient(90deg, 
    rgba(var(--v-theme-primary), 0.2) 0%, 
    rgba(var(--v-theme-primary), 0.1) 50%, 
    rgba(var(--v-theme-primary), 0.05) 100%);
  border-radius: 4px;
  border: 1px dashed rgba(var(--v-theme-primary), 0.3);
}

.target-category {
  font-size: 0.875rem;
  font-weight: 500;
}

.target-amount {
  font-size: 0.875rem;
  font-weight: 600;
}

.progress-container {
  margin-top: 8px;
}

.progress-text {
  font-size: 0.75rem;
}

.progress-percentage {
  font-size: 0.75rem;
  font-weight: 500;
}

.target-edit-item {
  padding: 8px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  background-color: rgba(var(--v-theme-surface-variant), 0.1);
}

.averages-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background-color: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 4px;
}

.average-item {
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.05);
}

.average-item:last-child {
  border-bottom: none;
}

.hover-elevate {
  transition: box-shadow 0.3s ease;
}

.hover-elevate:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>