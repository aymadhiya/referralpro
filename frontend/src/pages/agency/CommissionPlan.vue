<template>
  <div class="p-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Commission Plan</h1>
        <p class="text-surface-500 dark:text-surface-400 mt-1">Manage referral partner tiers and commission rules.</p>
      </div>
    </div>

    <TabView class="custom-tabview">
      <!-- Tiers Tab -->
      <TabPanel header="Partner Tiers">
        <div class="flex justify-end mb-4">
             <Button label="Add Tier" icon="pi pi-plus" @click="openTierDialog()" />
        </div>
        
        <div class="bg-white rounded-xl shadow-sm border border-surface-200 dark:border-surface-700 overflow-hidden">
            <DataTable :value="tiers" :loading="loadingTiers" responsiveLayout="scroll"
                :pt="{
                    table: { class: 'min-w-full' },
                    thead: { class: 'bg-surface-50' },
                    bodyRow: ({ context }) => ({
                        class: `hover:bg-surface-50 transition-colors ${context.selected ? 'bg-primary-50' : ''}`
                    })
                }"
            >
              <template #empty>
                  <div class="text-center p-8 text-slate-500">No tiers found. Add one to get started.</div>
              </template>
              <Column field="tier_name" header="Tier Name">
                <template #body="slotProps">
                    <span class="font-semibold text-surface-700 dark:text-surface-0">{{ slotProps.data.tier_name }}</span>
                </template>
              </Column>
              <Column field="is_default" header="Default">
                <template #body="slotProps">
                  <span v-if="slotProps.data.is_default" class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold">
                    Default
                  </span>
                  <span v-else class="text-slate-400 text-xs font-medium">No</span>
                </template>
              </Column>
              <Column header="Actions" alignFrozen="right" frozen style="width: 120px">
                <template #body="slotProps">
                     <div class="flex items-center gap-2">
                        <Button 
                            icon="pi pi-pencil"
                            text
                            rounded
                            severity="secondary"
                            @click="openTierDialog(slotProps.data)"
                            class="!p-2"
                        />
                        <Button 
                            icon="pi pi-trash"
                            text
                            rounded
                            severity="danger"
                            @click="confirmDeleteTier(slotProps.data)"
                            class="!p-2"
                        />
                    </div>
                </template>
              </Column>
            </DataTable>
        </div>
      </TabPanel>

      <!-- Rules Tab -->
      <TabPanel header="Commission Rules">
        <div class="flex justify-end mb-4">
             <Button label="Add Rule" icon="pi pi-plus" @click="openRuleDialog()" />
        </div>
        
        <div class="bg-white rounded-xl shadow-sm border border-surface-200 dark:border-surface-700 overflow-hidden">
            <DataTable :value="rules" :loading="loadingRules" responsiveLayout="scroll"
                :pt="{
                    table: { class: 'min-w-full' },
                    thead: { class: 'bg-surface-50' },
                    bodyRow: ({ context }) => ({
                        class: `hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors`
                    })
                }"
            >
              <template #empty>
                  <div class="text-center p-8 text-slate-500">No rules found. Add one to get started.</div>
              </template>
              <Column field="tier" header="Tier">
                  <template #body="slotProps">
                      <span class="font-medium text-surface-700 dark:text-surface-0">{{ getTierName(slotProps.data.tier) }}</span>
                  </template>
              </Column>
              <Column field="lead_status" header="Lead Status">
                 <template #body="slotProps">
                     <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                        {{ getLeadStatusLabel(slotProps.data.lead_status) }}
                     </span>
                 </template>
              </Column>
              <Column field="calculation_metric" header="Metric" style="width: 140px">
                  <template #body="slotProps">
                      <span class="text-xs text-slate-600">{{ slotProps.data.calculation_metric || 'Lead Count' }}</span>
                  </template>
              </Column>
              <Column field="calculation_period" header="Period" style="width: 120px">
                  <template #body="slotProps">
                      <span class="text-xs text-slate-600">{{ slotProps.data.calculation_period || 'Monthly' }}</span>
                  </template>
              </Column>
              <Column field="is_tiered" header="Mode" style="width: 100px">
                  <template #body="slotProps">
                      <span v-if="slotProps.data.is_tiered" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-purple-100 text-purple-700">
                          Tiered
                      </span>
                      <span v-else class="text-xs text-slate-500">Simple</span>
                  </template>
              </Column>
              <Column field="value" header="Commission">
                  <template #body="slotProps">
                      <span v-if="slotProps.data.is_tiered" class="text-xs text-blue-600 font-medium">Range Based</span>
                      <span v-else-if="slotProps.data.commission_type === 'Percentage'" class="font-mono text-slate-700">{{ slotProps.data.value }}%</span>
                      <span v-else class="font-mono text-slate-700">{{ formatCurrency(slotProps.data.value) }}</span>
                  </template>
              </Column>
              <Column header="Actions" alignFrozen="right" frozen style="width: 120px">
                <template #body="slotProps">
                     <div class="flex items-center gap-2">
                        <Button 
                            icon="pi pi-pencil"
                            text
                            rounded
                            severity="secondary"
                            @click="openRuleDialog(slotProps.data)"
                            class="!p-2"
                        />
                        <Button 
                            icon="pi pi-trash"
                            text
                            rounded
                            severity="danger"
                            @click="confirmDeleteRule(slotProps.data)"
                            class="!p-2"
                        />
                    </div>
                </template>
              </Column>
            </DataTable>
        </div>
      </TabPanel>
    </TabView>

    <!-- Tier Dialog -->
    <Dialog v-model:visible="tierDialogVisible" :header="editingTier.name ? 'Edit Tier' : 'Add Tier'" modal class="w-full max-w-md" :pt="{ root: { class: 'bg-white rounded-xl' } }">
      <div class="space-y-5 pt-2">
        <div class="space-y-1.5">
            <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tier Name</label>
            <InputText v-model="editingTier.tier_name" autofocus required class="w-full font-medium" placeholder="e.g. Gold Partner" />
        </div>
        
        <div class="bg-slate-50 rounded-lg p-3 border border-slate-100 mt-2">
            <div class="flex items-center gap-2">
                 <Checkbox v-model="editingTier.is_default" :binary="true" inputId="isDefault" />
                 <label for="isDefault" class="text-sm font-semibold text-slate-700 cursor-pointer select-none">Set as Default Tier</label>
            </div>
             <p class="text-xs text-slate-500 pl-8 mt-1">New partners will automatically be assigned this tier.</p>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 pt-4">
            <Button label="Cancel" text @click="tierDialogVisible = false" class="font-semibold" />
            <Button label="Save" @click="saveTier" class="px-6 font-bold" />
        </div>
      </template>
    </Dialog>

    <!-- Rule Dialog -->
    <Dialog v-model:visible="ruleDialogVisible" :header="editingRule.name ? 'Edit Rule' : 'Add Rule'" modal class="w-full max-w-2xl" :pt="{ root: { class: 'bg-white rounded-xl' } }">
       <div class="space-y-5 pt-2">
           <div class="grid grid-cols-2 gap-4">
               <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Tier</label>
                    <Dropdown v-model="editingRule.tier" :options="tiers" optionLabel="tier_name" optionValue="name" placeholder="Select a Tier" class="w-full" />
               </div>
               
               <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Lead Status</label>
                    <Dropdown v-model="editingRule.lead_status" :options="leadStatuses" optionLabel="label" optionValue="name" placeholder="Select a Status" class="w-full" />
               </div>
           </div>

           <!-- Calculation Setup -->
           <div class="bg-blue-50 p-4 rounded-lg border border-blue-100 space-y-4">
               <h4 class="text-xs font-bold text-blue-900 uppercase tracking-wider">Calculation Setup</h4>
               <div class="grid grid-cols-2 gap-4">
                   <div class="space-y-1.5">
                        <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Metric</label>
                        <Dropdown v-model="editingRule.calculation_metric" :options="['Lead Count', 'Total Deal Value']" placeholder="Select Metric" class="w-full" />
                   </div>
                   <div class="space-y-1.5">
                        <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Period</label>
                        <Dropdown v-model="editingRule.calculation_period" :options="['Monthly', 'Quarterly', 'Yearly', 'Lifetime']" placeholder="Select Period" class="w-full" />
                   </div>
               </div>
           </div>

           <!-- Tiered Toggle -->
           <div class="bg-slate-50 rounded-lg p-3 border border-slate-100">
               <div class="flex items-center gap-2">
                    <Checkbox v-model="editingRule.is_tiered" :binary="true" inputId="isTiered" />
                    <label for="isTiered" class="text-sm font-semibold text-slate-700 cursor-pointer select-none">Enable Tiered Commission (Range Based)</label>
               </div>
                <p class="text-xs text-slate-500 pl-8 mt-1">Different commission rates based on performance thresholds</p>
           </div>

           <!-- Simple Commission (when not tiered) -->
           <div v-if="!editingRule.is_tiered" class="bg-slate-50 p-4 rounded-lg border border-slate-100 space-y-4">
               <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Commission Type</label>
                    <SelectButton v-model="editingRule.commission_type" :options="['Percentage', 'Fixed Amount']" class="w-full" :pt="{ button: { class: 'flex-1' } }" />
               </div>
               <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">
                        {{ editingRule.commission_type === 'Percentage' ? 'Percentage Value' : 'Commission Amount' }}
                    </label>
                    <div class="relative">
                        <InputNumber 
                            v-if="editingRule.commission_type === 'Percentage'"
                            v-model="editingRule.value" 
                            :min="0" 
                            :max="100" 
                            suffix="%" 
                            class="w-full" 
                            placeholder="Enter percentage"
                        />
                        <InputNumber 
                            v-else
                            v-model="editingRule.value" 
                            mode="currency" 
                            currency="USD" 
                            locale="en-US" 
                            :minFractionDigits="0"
                            class="w-full" 
                            placeholder="Enter amount"
                        />
                    </div>
               </div>
           </div>

           <!-- Tiered Thresholds Table -->
           <div v-else class="space-y-3">
               <div class="flex items-center justify-between">
                   <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Threshold Ranges</label>
                   <Button label="Add Range" icon="pi pi-plus" size="small" @click="addThreshold" />
               </div>
               
               <div v-if="editingRule.thresholds.length === 0" class="text-center p-8 bg-slate-50 rounded-lg border border-slate-200">
                   <p class="text-slate-500 text-sm">No thresholds defined. Click "Add Range" to create one.</p>
               </div>

               <div v-else class="space-y-2">
                   <div v-for="(threshold, index) in editingRule.thresholds" :key="index" 
                        class="bg-white p-4 rounded-lg border border-slate-200 space-y-3">
                       <div class="flex items-center justify-between mb-2">
                           <span class="text-xs font-bold text-slate-400">Range {{ index + 1 }}</span>
                           <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="removeThreshold(index)" />
                       </div>
                       
                       <div class="grid grid-cols-2 gap-3">
                           <div class="space-y-1">
                               <label class="text-xs font-medium text-slate-500">From</label>
                               <InputNumber v-model="threshold.threshold_from" :min="0" class="w-full" />
                           </div>
                           <div class="space-y-1">
                               <label class="text-xs font-medium text-slate-500">To</label>
                               <InputNumber v-model="threshold.threshold_to" :min="0" class="w-full" />
                           </div>
                       </div>

                       <div class="grid grid-cols-2 gap-3">
                           <div class="space-y-1">
                               <label class="text-xs font-medium text-slate-500">Type</label>
                               <Dropdown v-model="threshold.commission_type" :options="['Percentage', 'Fixed Amount']" class="w-full" />
                           </div>
                           <div class="space-y-1">
                               <label class="text-xs font-medium text-slate-500">Value</label>
                               <InputNumber 
                                   v-if="threshold.commission_type === 'Percentage'"
                                   v-model="threshold.value" 
                                   :min="0" 
                                   :max="100" 
                                   suffix="%" 
                                   class="w-full"
                               />
                               <InputNumber 
                                   v-else
                                   v-model="threshold.value" 
                                   mode="currency" 
                                   currency="USD" 
                                   :minFractionDigits="0"
                                   class="w-full"
                               />
                           </div>
                       </div>
                   </div>
               </div>
           </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 pt-4">
            <Button label="Cancel" text @click="ruleDialogVisible = false" class="font-semibold" />
            <Button label="Save" @click="saveRule" class="px-6 font-bold" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Dropdown from 'primevue/dropdown'
import SelectButton from 'primevue/selectbutton'
import { Pencil, Trash2 } from 'lucide-vue-next'

// --- State ---
const tiers = ref([])
const rules = ref([])
const leadStatuses = ref([])
const loadingTiers = ref(false)
const loadingRules = ref(false)

// Dialogs
const tierDialogVisible = ref(false)
const ruleDialogVisible = ref(false)

const editingTier = ref({ name: null, tier_name: '', is_default: false })
const editingRule = ref({ 
    name: null, 
    tier: null, 
    lead_status: null, 
    calculation_metric: 'Lead Count',
    calculation_period: 'Monthly',
    commission_type: 'Percentage', 
    value: 0,
    is_tiered: false,
    thresholds: []
})

// --- Resources ---

// Fetch Tiers
const fetchTiers = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Referral Partner Tier',
        fields: JSON.stringify(['name', 'tier_name', 'is_default']),
        order_by: 'creation desc'
    },
    onSuccess: (data) => {
        tiers.value = data || []
    }
})

// Fetch Rules
const fetchRules = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Commission Rule',
        fields: JSON.stringify(['name', 'tier', 'lead_status', 'calculation_metric', 'calculation_period', 'commission_type', 'value', 'is_tiered'])
    },
    onSuccess: (data) => {
        rules.value = data || []
    }
})

// Fetch Lead Statuses (for dropdown)
const fetchLeadStatuses = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Lead Status',
        fields: JSON.stringify(['name', 'label']),
        order_by: 'sequence asc'
    },
    onSuccess: (data) => {
        leadStatuses.value = data || []
    }
})

// Save Tier
const tierSaver = createResource({
    url: 'referralpro.api.agency.doc.save_doc',
    onSuccess: () => {
        tierDialogVisible.value = false
        fetchTiers.fetch()
    }
})

// Delete Tier
const tierDeleter = createResource({
    url: 'referralpro.api.agency.doc.delete_doc',
    onSuccess: () => {
        fetchTiers.fetch()
    }
})

// Save Rule
const ruleSaver = createResource({
    url: 'referralpro.api.agency.doc.save_doc',
    onSuccess: () => {
        ruleDialogVisible.value = false
        fetchRules.fetch()
    }
})

// Delete Rule
const ruleDeleter = createResource({
    url: 'referralpro.api.agency.doc.delete_doc',
    onSuccess: () => {
        fetchRules.fetch()
    }
})

// --- Methods ---

onMounted(() => {
    loadingTiers.value = true
    fetchTiers.fetch().then(() => loadingTiers.value = false)
    
    loadingRules.value = true
    fetchRules.fetch().then(() => loadingRules.value = false)
    
    fetchLeadStatuses.fetch()
})


// Tier Methods
const openTierDialog = (tier = null) => {
    if (tier) {
        editingTier.value = { ...tier, is_default: !!tier.is_default }
    } else {
        editingTier.value = { name: null, tier_name: '', is_default: false }
    }
    tierDialogVisible.value = true
}

const saveTier = () => {
    if (!editingTier.value.tier_name) return
    
    tierSaver.submit({
        doctype: 'Referral Partner Tier',
        doc: {
            name: editingTier.value.name,
            tier_name: editingTier.value.tier_name,
            is_default: editingTier.value.is_default ? 1 : 0
        }
    })
}

const confirmDeleteTier = (tier) => {
    if (confirm(`Are you sure you want to delete tier "${tier.tier_name}"?`)) {
        tierDeleter.submit({
            doctype: 'Referral Partner Tier',
            name: tier.name
        })
    }
}

// Rule Methods
const openRuleDialog = async (rule = null) => {
    if (rule) {
        // Fetch full document with child table
        const fullDoc = await createResource({
            url: 'referralpro.api.agency.doc.get_doc',
            params: { doctype: 'Commission Rule', name: rule.name }
        }).fetch()
        
        editingRule.value = {
            ...fullDoc,
            thresholds: fullDoc.thresholds || []
        }
    } else {
        editingRule.value = { 
            name: null, 
            tier: null, 
            lead_status: null, 
            calculation_metric: 'Lead Count',
            calculation_period: 'Monthly',
            commission_type: 'Percentage', 
            value: 0,
            is_tiered: false,
            thresholds: []
        }
    }
    ruleDialogVisible.value = true
}

const saveRule = () => {
    if (!editingRule.value.tier || !editingRule.value.lead_status) return
    
    ruleSaver.submit({
        doctype: 'Commission Rule',
        doc: {
            name: editingRule.value.name,
            tier: editingRule.value.tier,
            lead_status: editingRule.value.lead_status,
            calculation_metric: editingRule.value.calculation_metric,
            calculation_period: editingRule.value.calculation_period,
            commission_type: editingRule.value.commission_type,
            value: editingRule.value.value,
            is_tiered: editingRule.value.is_tiered ? 1 : 0,
            thresholds: editingRule.value.is_tiered ? editingRule.value.thresholds : []
        }
    })
}

const addThreshold = () => {
    editingRule.value.thresholds.push({
        threshold_from: 0,
        threshold_to: 0,
        commission_type: 'Percentage',
        value: 0
    })
}

const removeThreshold = (index) => {
    editingRule.value.thresholds.splice(index, 1)
}

const confirmDeleteRule = (rule) => {
    if (confirm('Are you sure you want to delete this rule?')) {
        ruleDeleter.submit({
            doctype: 'Commission Rule',
            name: rule.name
        })
    }
}

// Helpers
const getTierName = (name) => {
    const t = tiers.value.find(x => x.name === name)
    return t ? t.tier_name : name
}

const getLeadStatusLabel = (name) => {
    const s = leadStatuses.value.find(x => x.name === name)
    return s ? s.label : name
}

const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

</script>

<style scoped>
:deep(.custom-tabview .p-tabview-nav) {
    background: transparent;
    border-bottom: 2px solid #f1f5f9;
}
:deep(.custom-tabview .p-tabview-header) {
    background: transparent;
}
:deep(.custom-tabview .p-tabview-nav-link) {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    @apply text-surface-500 dark:text-surface-400;
    font-weight: 500;
    transition: all 0.2s;
    margin-bottom: -2px;
}
:deep(.custom-tabview .p-tabview-selected .p-tabview-nav-link) {
    @apply text-surface-900 dark:text-surface-0 border-surface-900 dark:border-surface-0;
}
:deep(.p-datatable-header) {
    background: transparent;
    border: none;
}
</style>
