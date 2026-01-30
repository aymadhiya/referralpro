<script setup>
import { ref, onMounted, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { Search, Filter, ArrowUpRight, Download } from 'lucide-vue-next'

const router = useRouter()
const leads = ref([])
const leadStatuses = ref([])
const filters = ref({
    global: { value: null }
})

const fetchLeads = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Referral Lead',
        fields: JSON.stringify(['name', 'first_name', 'last_name', 'email', 'phone', 'status', 'partner', 'creation', 'deal_value']),
        order_by: 'creation desc'
    },
    onSuccess: (data) => {
        leads.value = data || []
    }
})

const fetchStatuses = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Lead Status',
        fields: JSON.stringify(['name', 'label', 'color'])
    },
    onSuccess: (data) => {
        leadStatuses.value = data || []
    }
})

onMounted(() => {
    fetchLeads.fetch()
    fetchStatuses.fetch()
})

const getStatusLabel = (name) => {
    const s = leadStatuses.value.find(x => x.name === name)
    return s ? s.label : name
}

const getStatusColor = (name) => {
    const s = leadStatuses.value.find(x => x.name === name)
    return s ? s.color : '#64748b'
}
</script>

<template>
  <div class="p-6 max-w-[1600px] mx-auto space-y-6 font-sans">
    <!-- Header Area -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Referral Leads</h1>
            <p class="text-slate-500 font-medium">Track and manage leads submitted by your partners.</p>
        </div>
        <div class="flex gap-2">
             <Button 
                label="Export" 
                icon="pi pi-download" 
                severity="secondary" 
                outlined
            />
        </div>
    </div>

    <!-- List Area -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden min-h-[400px]">
        <DataTable 
            v-model:filters="filters"
            :value="leads" 
            :loading="fetchLeads.loading"
            paginator :rows="20"
            dataKey="name"
            filterDisplay="menu"
            :globalFilterFields="['first_name', 'last_name', 'email', 'partner']"
            class="p-datatable-sm"
            responsiveLayout="scroll"
            :pt="{
                thead: { class: 'bg-slate-50' },
                header: { class: 'bg-white border-b border-slate-100 p-4' }
            }"
        >
            <template #header>
                <div class="flex flex-col sm:flex-row justify-between items-center gap-4">
                    <span class="relative w-full sm:w-80">
                        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="16" />
                        <InputText v-model="filters['global'].value" placeholder="Search leads..." class="w-full pl-9 py-2 text-sm" />
                    </span>
                    <div class="flex gap-2 w-full sm:w-auto">
                        <Button icon="pi pi-filter" text severity="secondary" rounded />
                        <Button icon="pi pi-refresh" text severity="secondary" rounded @click="fetchLeads.reload()" />
                    </div>
                </div>
            </template>

            <template #empty>
                <div class="text-center p-20 space-y-4">
                    <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto text-slate-300">
                        <ArrowUpRight :size="32" />
                    </div>
                    <h3 class="text-lg font-bold text-slate-900">No leads found</h3>
                    <p class="text-slate-500 max-w-xs mx-auto text-sm">Your partners haven't submitted any referrals yet.</p>
                </div>
            </template>

            <Column field="name" header="ID" class="font-mono text-[10px] text-slate-400" style="width: 100px" />
            
            <Column header="Lead Name" style="min-width: 200px">
                <template #body="slotProps">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-800 text-sm">{{ slotProps.data.first_name }} {{ slotProps.data.last_name }}</span>
                        <span class="text-xs text-slate-400 font-medium">{{ slotProps.data.email || 'No email' }}</span>
                    </div>
                </template>
            </Column>

            <Column field="partner" header="Referred By" style="min-width: 180px">
                <template #body="slotProps">
                    <div class="flex items-center gap-2">
                        <div class="w-6 h-6 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center text-[10px] font-bold">
                            {{ slotProps.data.partner ? slotProps.data.partner.charAt(0).toUpperCase() : '?' }}
                        </div>
                        <span class="text-sm font-medium text-slate-600">{{ slotProps.data.partner }}</span>
                    </div>
                </template>
            </Column>

            <Column field="deal_value" header="Deal Value" style="width: 120px">
                <template #body="slotProps">
                    <span class="text-sm font-bold text-slate-900">
                        {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(slotProps.data.deal_value || 0) }}
                    </span>
                </template>
            </Column>

            <Column field="status" header="Status" style="min-width: 140px">
                <template #body="slotProps">
                    <div 
                        class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider"
                        :style="{ backgroundColor: getStatusColor(slotProps.data.status) + '15', color: getStatusColor(slotProps.data.status) }"
                    >
                         <div class="w-1.5 h-1.5 rounded-full mr-1.5" :style="{ backgroundColor: getStatusColor(slotProps.data.status) }"></div>
                         {{ getStatusLabel(slotProps.data.status) }}
                    </div>
                </template>
            </Column>

            <Column field="creation" header="Date" style="width: 120px">
                <template #body="slotProps">
                    <span class="text-xs text-slate-500 font-medium">
                        {{ new Date(slotProps.data.creation).toLocaleDateString() }}
                    </span>
                </template>
            </Column>

            <Column header="Actions" alignFrozen="right" frozen style="width: 60px">
                <template #body="slotProps">
                    <Button icon="pi pi-eye" text rounded severity="secondary" size="small" @click="router.push(`/agency/referrals/${slotProps.data.name}`)" />
                </template>
            </Column>
        </DataTable>
    </div>
  </div>
</template>

<style scoped>
:deep(.p-datatable-thead > tr > th) {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
}
</style>
