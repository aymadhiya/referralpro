<script setup>
import { ref, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Calendar from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { ArrowLeft, Send, CheckCircle2, Building2 } from 'lucide-vue-next'

const router = useRouter()
const toast = useToast()

const agencies = ref([])
const selectedAgency = ref(null)
const customFields = ref([])
const form = ref({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    notes: ''
})
const customValues = ref({})
const submitting = ref(false)
const errors = ref({})

const validate = () => {
    errors.value = {}
    
    if (!form.value.first_name) errors.value.first_name = 'First name is required'
    if (!form.value.last_name) errors.value.last_name = 'Last name is required'
    
    customFields.value.forEach(field => {
        if (field.is_required && !customValues.value[field.fieldname]) {
            errors.value[field.fieldname] = `${field.label} is required`
        }
    })
    
    return Object.keys(errors.value).length === 0
}

const fetchAgencies = createResource({
    url: 'referralpro.api.partner.partner.get_partner_organizations',
    onSuccess: (data) => {
        agencies.value = data || []
        if (agencies.value.length === 1) {
            selectedAgency.value = agencies.value[0]
        }
    }
})

const fetchCustomFields = createResource({
    url: 'referralpro.api.partner.referral.get_lead_form_fields',
    makeParams(values) {
        return { agency_name: selectedAgency.value?.name }
    },
    onSuccess: (data) => {
        customFields.value = data || []
        // Initialize custom values
        customValues.value = {}
        customFields.value.forEach(f => {
            customValues.value[f.fieldname] = null
        })
    }
})

watch(selectedAgency, (newAgency) => {
    if (newAgency) {
        fetchCustomFields.fetch()
    } else {
        customFields.value = []
    }
})

const handleSubmit = async () => {
    if (!selectedAgency.value) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Please select an agency' })
        return
    }

    if (!validate()) {
        toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Please check the required fields' })
        return
    }

    submitting.value = true
    try {
        const resource = createResource({
            url: 'referralpro.api.partner.referral.submit_referral',
            params: {
                agency_name: selectedAgency.value.name,
                lead_data: form.value,
                custom_values: customValues.value
            },
            onSuccess: (data) => {
                toast.add({ severity: 'success', summary: 'Success', detail: 'Referral submitted successfully' })
                setTimeout(() => {
                    router.push('/partner/leads')
                }, 1000)
            },
            onError: (err) => {
                toast.add({ severity: 'error', summary: 'Error', detail: err.message || 'Failed to submit referral' })
            }
        })
        await resource.submit()
    } finally {
        submitting.value = false
    }
}

const getDropdownOptions = (optionsStr) => {
    if (!optionsStr) return []
    return optionsStr.split('\n').map(o => ({ label: o.trim(), value: o.trim() })).filter(o => o.value)
}

onMounted(() => {
    fetchAgencies.fetch()
})
</script>

<template>
  <div class="min-h-screen bg-surface-50 p-6 lg:p-12 font-sans">
    <Toast />
    <div class="max-w-3xl mx-auto">
        <!-- Header -->
        <div class="mb-10 flex items-center justify-between">
            <div class="flex items-center gap-4">
                <Button 
                    icon="pi pi-arrow-left" 
                    text 
                    severity="secondary" 
                    @click="router.back()"
                />
                <div>
                    <h1 class="text-3xl font-black text-slate-900 tracking-tight">New Referral</h1>
                    <p class="text-slate-500 font-medium">Capture details for your new potential lead.</p>
                </div>
            </div>
        </div>

        <!-- Form View -->
        <div class="space-y-6">
            
            <!-- Agency Selection (if multiple) -->
            <div v-if="agencies.length > 1" class="bg-blue-600 rounded-[2rem] p-8 text-white shadow-lg shadow-blue-200 mb-8">
                <div class="flex items-start gap-4 mb-6">
                    <div class="p-3 bg-white/10 rounded-xl">
                        <Building2 :size="24" />
                    </div>
                    <div>
                        <h3 class="text-lg font-bold">Select Agency</h3>
                        <p class="text-blue-100 text-sm">Choose the agency you are referring this lead to.</p>
                    </div>
                </div>
                <Dropdown 
                    v-model="selectedAgency" 
                    :options="agencies" 
                    optionLabel="organization_name" 
                    placeholder="Select Agency"
                    class="w-full"
                />
            </div>

            <div v-if="selectedAgency" class="bg-white rounded-[2.5rem] border border-slate-200 shadow-sm overflow-hidden min-h-[500px]">
                <!-- Form Sections -->
                <div class="p-8 lg:p-10 space-y-10">
                    
                    <!-- Basic Information -->
                    <section class="space-y-6">
                        <div class="flex items-center gap-3">
                            <span class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-black">01</span>
                            <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest">Basic Information</h3>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">First Name *</label>
                                <InputText v-model="form.first_name" :invalid="!!errors.first_name" />
                                <small v-if="errors.first_name" class="p-error">{{ errors.first_name }}</small>
                            </div>
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Last Name *</label>
                                <InputText v-model="form.last_name" :invalid="!!errors.last_name" />
                                <small v-if="errors.last_name" class="p-error">{{ errors.last_name }}</small>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Email Address</label>
                                <InputText v-model="form.email" />
                            </div>
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Phone Number</label>
                                <InputText v-model="form.phone" />
                            </div>
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Deal Value (Optional)</label>
                                <InputNumber v-model="form.deal_value" mode="currency" currency="USD" locale="en-US" class="w-full" />
                            </div>
                        </div>
                    </section>

                    <!-- Custom Fields Section -->
                    <section v-if="customFields.length > 0" class="space-y-6 pt-10 border-t border-slate-50">
                         <div class="flex items-center gap-3">
                            <span class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-black">02</span>
                            <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest">Additional Details</h3>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div v-for="field in customFields" :key="field.fieldname" class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">
                                    {{ field.label }} {{ field.is_required ? '*' : '' }}
                                </label>
                                
                                <!-- Render Based on Type -->
                                <InputText v-if="['Data'].includes(field.fieldtype)" 
                                    v-model="customValues[field.fieldname]" 
                                    :invalid="!!errors[field.fieldname]"
                                />
                                
                                <InputNumber v-else-if="['Int', 'Float'].includes(field.fieldtype)" 
                                    v-model="customValues[field.fieldname]" 
                                    :invalid="!!errors[field.fieldname]"
                                    class="w-full"
                                />

                                <Dropdown v-else-if="field.fieldtype === 'Select'" 
                                    v-model="customValues[field.fieldname]"
                                    :options="getDropdownOptions(field.options)"
                                    optionLabel="label"
                                    optionValue="value"
                                    placeholder="Select Option"
                                    :invalid="!!errors[field.fieldname]"
                                    class="w-full"
                                />

                                <Calendar v-else-if="field.fieldtype === 'Date'"
                                    v-model="customValues[field.fieldname]"
                                    dateFormat="yy-mm-dd"
                                    :invalid="!!errors[field.fieldname]"
                                    class="w-full"
                                />

                                <Textarea v-else-if="field.fieldtype === 'Small Text'"
                                    v-model="customValues[field.fieldname]"
                                    rows="3"
                                    :invalid="!!errors[field.fieldname]"
                                    class="w-full"
                                />
                                <small v-if="errors[field.fieldname]" class="p-error">{{ errors[field.fieldname] }}</small>
                            </div>
                        </div>
                    </section>

                    <!-- Notes Section -->
                    <section class="space-y-6 pt-10 border-t border-slate-50">
                        <div class="flex items-center gap-3">
                            <span class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-black">
                                {{ customFields.length > 0 ? '03' : '02' }}
                            </span>
                            <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest">Internal Notes</h3>
                        </div>
                        <Textarea 
                            v-model="form.notes" 
                            placeholder="Add any extra context for the agency success team..."
                            rows="4" 
                            class="w-full" 
                        />
                    </section>
                </div>

                <!-- Footer Action -->
                <div class="px-8 lg:px-10 py-6 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                    <p class="text-xs text-slate-400 font-medium">Fields marked with * are mandatory.</p>
                    <Button 
                        label="Submit Referral" 
                        icon="pi pi-send" 
                        iconPos="right" 
                        @click="handleSubmit"
                        :loading="submitting"
                    />
                </div>
            </div>
            
            <!-- Loading State if Agency but no fields yet -->
            <div v-else-if="fetchAgencies.loading" class="flex flex-col items-center justify-center min-h-[400px]">
                <div class="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full mb-4"></div>
                <p class="text-slate-500 font-medium tracking-tight">Loading Portal...</p>
            </div>
        </div>
    </div>
  </div>
</template>
