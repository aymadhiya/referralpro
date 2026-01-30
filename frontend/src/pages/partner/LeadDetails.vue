<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import Button from 'primevue/button'
import { ArrowLeft, User, Mail, Phone, Calendar as CalendarIcon, FileText, Building2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const leadId = route.params.id
const lead = ref(null)

const fetchLead = createResource({
    url: 'referralpro.api.partner.referral.get_lead_details',
    params: { name: leadId },
    onSuccess: (data) => {
        lead.value = data
    }
})

onMounted(() => {
    fetchLead.fetch()
})
</script>

<template>
  <div class="p-6 lg:p-12 max-w-4xl mx-auto space-y-8 font-sans">
    <div class="flex items-center gap-4">
        <Button icon="pi pi-arrow-left" text severity="secondary" @click="router.back()" />
        <div>
            <h1 class="text-3xl font-black text-slate-900 tracking-tight">Referral Details</h1>
            <p class="text-slate-500 font-medium">{{ leadId }}</p>
        </div>
    </div>

    <div v-if="fetchLead.loading" class="flex flex-col items-center justify-center min-h-[400px]">
        <div class="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full mb-4"></div>
        <p class="text-slate-500 font-medium">Loading details...</p>
    </div>

    <div v-else-if="lead" class="space-y-6">
        <!-- Lead Info Card -->
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-8 space-y-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-8 border-b border-slate-100">
                <div class="flex items-center gap-4">
                    <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center">
                        <User :size="32" />
                    </div>
                    <div>
                        <h2 class="text-2xl font-black text-slate-900">{{ lead.first_name }} {{ lead.last_name }}</h2>
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider"
                            :style="{ backgroundColor: lead.status_color + '20', color: lead.status_color }">
                            {{ lead.status_label }}
                        </span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="space-y-4">
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">Contact Information</h3>
                    <div class="space-y-3">
                        <div class="flex items-center gap-3 text-slate-600">
                            <Mail :size="18" class="text-slate-400" />
                            <span class="font-medium">{{ lead.email || 'No email provided' }}</span>
                        </div>
                        <div class="flex items-center gap-3 text-slate-600">
                            <Phone :size="18" class="text-slate-400" />
                            <span class="font-medium">{{ lead.phone || 'No phone provided' }}</span>
                        </div>
                    </div>
                </div>
                <div class="space-y-4">
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">Submission Details</h3>
                    <div class="space-y-3">
                         <div class="flex items-center gap-3 text-slate-600">
                            <CalendarIcon :size="18" class="text-slate-400" />
                            <span class="font-medium">Submitted on {{ new Date(lead.creation).toLocaleDateString() }}</span>
                        </div>
                        <div class="flex items-center gap-3 text-slate-600">
                            <Building2 :size="18" class="text-slate-400" />
                            <span class="font-medium">Referred to {{ lead.agency_name }}</span>
                        </div>
                        <div class="flex items-center gap-3 text-slate-600">
                            <div class="w-[18px] text-center font-bold text-slate-400">$</div>
                            <span class="font-medium">Deal Value: {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(lead.deal_value || 0) }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="lead.notes" class="space-y-4 pt-8 border-t border-slate-100">
                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">Notes</h3>
                <p class="text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-100 italic">{{ lead.notes }}</p>
            </div>

            <div v-if="lead.custom_values && lead.custom_values.length > 0" class="space-y-4 pt-8 border-t border-slate-100">
                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">Custom Fields</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div v-for="val in lead.custom_values" :key="val.fieldname" class="space-y-1">
                        <span class="block text-xs font-bold text-slate-400">{{ val.label }}</span>
                        <span class="font-semibold text-slate-700">{{ val.value }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div v-else class="text-center py-20 bg-white rounded-xl border border-slate-200">
        <p class="text-slate-500 font-medium">Lead not found or you don't have access.</p>
        <Button label="Go back to list" @click="router.push('/partner/leads')" text class="mt-4" />
    </div>
  </div>
</template>
