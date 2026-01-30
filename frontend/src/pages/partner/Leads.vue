<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { Plus, Search, Filter, ArrowUpRight } from 'lucide-vue-next'
import InputText from 'primevue/inputtext'

const router = useRouter()
const referrals = ref([])
const filters = ref({
    global: { value: null }
})

const fetchReferrals = createResource({
    url: 'referralpro.api.partner.referral.get_my_referrals',
    onSuccess: (data) => {
        referrals.value = data || []
    }
})

onMounted(() => {
    fetchReferrals.fetch()
})

const getStatusSeverity = (status) => {
    // Simple logic, can be improved based on labels
    const s = status?.toLowerCase() || ''
    if (s.includes('converted') || s.includes('win') || s.includes('success')) return 'success'
    if (s.includes('reject') || s.includes('lost')) return 'danger'
    if (s.includes('progress') || s.includes('working')) return 'info'
    return 'warning'
}
</script>

<template>
  <div class="space-y-8 font-sans">
    <!-- Header Area -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-3xl font-black text-slate-900 tracking-tight">Referral Leads</h1>
            <p class="text-slate-500 font-medium">Manage and track all referrals you've submitted.</p>
        </div>
        <Button 
            label="Submit New Referral" 
            icon="pi pi-plus" 
            @click="router.push('/partner/leads/add')"
        />
    </div>

    <!-- Stats Overview (Optional, could fetch from API) -->
    
    <!-- List Area -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden min-h-[400px]">
        <DataTable 
            v-model:filters="filters"
            :value="referrals" 
            :loading="fetchReferrals.loading"
            paginator :rows="10"
            dataKey="name"
            filterDisplay="menu"
            :globalFilterFields="['first_name', 'last_name', 'email', 'agency_name']"
            class="p-datatable-sm"
            responsiveLayout="scroll"
        >
            <template #header>
                <div class="flex flex-col sm:flex-row justify-between items-center gap-4 py-2">
                    <span class="relative w-full sm:w-80">
                        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="18" />
                        <InputText v-model="filters['global'].value" placeholder="Search referrals..." class="w-full pl-10" />
                    </span>
                    <div class="flex gap-2 w-full sm:w-auto">
                        <Button icon="pi pi-filter" text severity="secondary" rounded />
                        <Button icon="pi pi-refresh" text severity="secondary" rounded @click="fetchReferrals.reload()" />
                    </div>
                </div>
            </template>

            <template #empty>
                <div class="text-center p-20 space-y-4">
                    <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto text-slate-300">
                        <ArrowUpRight :size="40" />
                    </div>
                    <h3 class="text-xl font-bold text-slate-900">No referrals found</h3>
                    <p class="text-slate-500 max-w-xs mx-auto">You haven't submitted any referrals yet. Submit your first one to start earning!</p>
                    <Button label="Submit Your First Referral" @click="router.push('/partner/leads/add')" text class="font-bold underline" />
                </div>
            </template>

            <Column field="name" header="Ref ID" class="font-mono text-xs text-slate-400" style="width: 120px" />
            
            <Column header="Lead Name" style="min-width: 200px">
                <template #body="slotProps">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-800">{{ slotProps.data.first_name }} {{ slotProps.data.last_name }}</span>
                        <span class="text-xs text-slate-400 font-medium">{{ slotProps.data.email || 'No email' }}</span>
                    </div>
                </template>
            </Column>

            <Column field="agency_name" header="Agency" style="min-width: 150px">
                <template #body="slotProps">
                    <div class="flex items-center gap-2">
                        <div class="w-6 h-6 rounded bg-emerald-50 text-emerald-600 flex items-center justify-center text-[10px] font-black uppercase">
                            {{ slotProps.data.agency_name?.charAt(0) }}
                        </div>
                        <span class="text-sm font-medium text-slate-600">{{ slotProps.data.agency_name }}</span>
                    </div>
                </template>
            </Column>

            <Column field="deal_value" header="Deal Value" style="width: 120px">
                <template #body="slotProps">
                    <span class="font-bold text-slate-900">
                        {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(slotProps.data.deal_value || 0) }}
                    </span>
                </template>
            </Column>

            <Column field="status" header="Status" style="min-width: 120px">
                <template #body="slotProps">
                    <div 
                        class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider"
                        :style="{ backgroundColor: slotProps.data.status_color + '20', color: slotProps.data.status_color }"
                    >
                         <div class="w-1.5 h-1.5 rounded-full mr-1.5" :style="{ backgroundColor: slotProps.data.status_color }"></div>
                         {{ slotProps.data.status_label }}
                    </div>
                </template>
            </Column>

            <Column field="creation" header="Submitted On" style="width: 150px">
                <template #body="slotProps">
                    <span class="text-xs text-slate-500 font-medium">
                        {{ new Date(slotProps.data.creation).toLocaleDateString() }}
                    </span>
                </template>
            </Column>

            <Column header="Actions" alignFrozen="right" frozen style="width: 80px">
                <template #body="slotProps">
                    <Button icon="pi pi-eye" text rounded severity="secondary" @click="router.push(`/partner/leads/${slotProps.data.name}`)" />
                </template>
            </Column>
        </DataTable>
    </div>
  </div>
</template>

<style scoped>
:deep(.p-datatable-thead > tr > th) {
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
</style>
