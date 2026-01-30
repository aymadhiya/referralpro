<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { DollarSign, Clock, CheckCircle } from 'lucide-vue-next'

const transactions = ref([])

// Resources
const fetchTransactions = createResource({
    url: 'referralpro.api.partner.referral.get_my_referrals', // Need specific API for transactions?
    // Wait, get_my_referrals returns Leads. We need a new generic list getter for partners or update permissions.
    // Let's rely on standard doc permission for now or create 'get_my_transactions'
})

// Let's create a specific API call for partner transactions to be safe/clean
const fetchPartnerTransactions = createResource({
    url: 'referralpro.api.partner.referral.get_my_transactions',
    onSuccess: (data) => {
        transactions.value = data || []
    }
})

onMounted(() => {
    fetchPartnerTransactions.fetch()
})

const getStatusSeverity = (status) => {
    switch (status) {
        case 'Paid': return 'success'
        case 'Approved': return 'info'
        case 'Rejected': return 'danger'
        case 'Pending': return 'warning'
        default: return 'secondary'
    }
}

const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

// Dialog Logic
const showDialog = ref(false)
const selectedTransaction = ref(null)

const openTransactionDialog = (transaction) => {
    selectedTransaction.value = transaction
    showDialog.value = true
}
</script>

<template>
  <div class="space-y-8 font-sans">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-3xl font-black text-slate-900 tracking-tight">Earnings & Payouts</h1>
            <p class="text-slate-500 font-medium">Track your commission history and payment status.</p>
        </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div class="space-y-1">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Total Paid</p>
                <h3 class="text-3xl font-black text-emerald-600">
                    {{ formatCurrency(transactions.filter(t => t.status === 'Paid').reduce((acc, t) => acc + t.amount, 0)) }}
                </h3>
            </div>
            <div class="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center">
                <DollarSign :size="28" />
            </div>
        </div>
         <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div class="space-y-1">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Pending Payout</p>
                <h3 class="text-3xl font-black text-blue-600">
                    {{ formatCurrency(transactions.filter(t => t.status === 'Approved').reduce((acc, t) => acc + t.amount, 0)) }}
                </h3>
            </div>
            <div class="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center">
                <CheckCircle :size="28" />
            </div>
        </div>
         <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div class="space-y-1">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Processing</p>
                <h3 class="text-3xl font-black text-amber-500">
                    {{ formatCurrency(transactions.filter(t => t.status === 'Pending').reduce((acc, t) => acc + t.amount, 0)) }}
                </h3>
            </div>
            <div class="w-14 h-14 bg-amber-50 text-amber-500 rounded-2xl flex items-center justify-center">
                <Clock :size="28" />
            </div>
        </div>
    </div>

    <!-- List -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden min-h-[400px]">
        <DataTable :value="transactions" :loading="fetchPartnerTransactions.loading" paginator :rows="10" class="p-datatable-sm" responsiveLayout="scroll">
             <template #empty>
                <div class="text-center p-20 text-slate-400">
                    <p class="font-medium">No transactions yet.</p>
                </div>
            </template>
            
            <Column field="date" header="Date" style="width: 150px">
                 <template #body="slotProps">
                    <span class="text-sm font-medium text-slate-600">{{ slotProps.data.date }}</span>
                </template>
            </Column>
            <Column field="referral_lead" header="Referral" style="min-width: 200px">
                <template #body="slotProps">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-800">{{ slotProps.data.lead_name || slotProps.data.referral_lead }}</span>
                        <span class="text-xs text-slate-400">{{ slotProps.data.note }}</span>
                    </div>
                </template>
            </Column>
            <Column field="amount" header="Commission" style="width: 150px">
                <template #body="slotProps">
                    <span class="font-black text-slate-900">{{ formatCurrency(slotProps.data.amount) }}</span>
                </template>
            </Column>
            <Column field="status" header="Status" style="width: 150px">
                <template #body="slotProps">
                    <div 
                        class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider"
                        :class="{
                            'bg-emerald-50 text-emerald-600': slotProps.data.status === 'Paid',
                            'bg-blue-50 text-blue-600': slotProps.data.status === 'Approved',
                            'bg-amber-50 text-amber-600': slotProps.data.status === 'Pending',
                            'bg-red-50 text-red-600': slotProps.data.status === 'Rejected'
                        }"
                    >
                         {{ slotProps.data.status }}
                    </div>
                </template>
            </Column>
            <Column header="Action" style="width: 100px" alignFrozen="right" frozen>
                <template #body="slotProps">
                    <Button icon="pi pi-eye" text rounded severity="secondary" @click="openTransactionDialog(slotProps.data)" />
                </template>
            </Column>
        </DataTable>
    </div>

    <!-- Transaction Detail Dialog -->
    <Dialog v-model:visible="showDialog" modal header="Transaction Details" :style="{ width: '450px' }">
        <div v-if="selectedTransaction" class="space-y-6 pt-2">
            
            <!-- Amount Header -->
            <div class="text-center p-6 bg-slate-50 rounded-xl border border-slate-100">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Commission Amount</p>
                <h2 class="text-4xl font-black text-slate-900">{{ formatCurrency(selectedTransaction.amount) }}</h2>
                <div class="mt-3">
                    <Tag :value="selectedTransaction.status" :severity="getStatusSeverity(selectedTransaction.status)" class="!text-xs !font-bold !px-3 !py-1" />
                </div>
            </div>

            <!-- Details List -->
            <div class="space-y-4">
                <div class="flex justify-between py-2 border-b border-slate-100">
                    <span class="text-sm font-medium text-slate-500">Transaction ID</span>
                    <span class="text-sm font-bold text-slate-900 font-mono">{{ selectedTransaction.name }}</span>
                </div>
                 <div class="flex justify-between py-2 border-b border-slate-100">
                    <span class="text-sm font-medium text-slate-500">Date</span>
                    <span class="text-sm font-bold text-slate-900">{{ selectedTransaction.date }}</span>
                </div>
                 <div class="flex justify-between py-2 border-b border-slate-100">
                    <span class="text-sm font-medium text-slate-500">Referral Lead</span>
                    <span class="text-sm font-bold text-slate-900">{{ selectedTransaction.lead_name || selectedTransaction.referral_lead }}</span>
                </div>
                 <div class="flex justify-between py-2 border-b border-slate-100">
                    <span class="text-sm font-medium text-slate-500">Commission Rule</span>
                    <span class="text-sm font-bold text-slate-900">{{ selectedTransaction.commission_rule_title || selectedTransaction.commission_rule || 'Standard' }}</span>
                </div>
            </div>

            <!-- Note -->
            <div v-if="selectedTransaction.note" class="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">Note from Agency</p>
                <p class="text-sm text-blue-800">{{ selectedTransaction.note }}</p>
            </div>
        </div>
        <template #footer>
            <Button label="Close" text severity="secondary" @click="showDialog = false" class="w-full" />
        </template>
    </Dialog>
  </div>
</template>
