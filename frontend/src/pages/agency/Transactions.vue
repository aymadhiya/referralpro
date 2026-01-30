<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import { Check, X, DollarSign, Clock } from 'lucide-vue-next'

const transactions = ref([])
const filters = ref({})

// Resources
const fetchTransactions = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Referral Transaction',
        fields: JSON.stringify(['name', 'partner', 'referral_lead', 'amount', 'status', 'date', 'note']),
        order_by: 'creation desc'
    },
    onSuccess: (data) => {
        transactions.value = data || []
    }
})

const transactionUpdater = createResource({
    url: 'referralpro.api.agency.doc.save_doc',
    onSuccess: () => {
        fetchTransactions.fetch()
        actionDialogVisible.value = false
    }
})

onMounted(() => {
    fetchTransactions.fetch()
})

// Actions
const actionDialogVisible = ref(false)
const selectedTransaction = ref(null)
const actionType = ref('approve') // approve, reject
const actionNote = ref('')

const openActionDialog = (trx, type) => {
    selectedTransaction.value = trx
    actionType.value = type
    actionNote.value = ''
    actionDialogVisible.value = true
}

const submitAction = () => {
    if (!selectedTransaction.value) return
    
    let newStatus = 'Pending'
    if (actionType.value === 'approve') newStatus = 'Approved'
    else if (actionType.value === 'reject') newStatus = 'Rejected'
    else if (actionType.value === 'pay') newStatus = 'Paid'
    
    transactionUpdater.submit({
        doctype: 'Referral Transaction',
        doc: {
            name: selectedTransaction.value.name,
            status: newStatus,
            note: actionNote.value || selectedTransaction.value.note
        }
    })
}

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
</script>

<template>
  <div class="p-6 max-w-[1600px] mx-auto space-y-6 font-sans">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Financial Transactions</h1>
            <p class="text-slate-500 font-medium">Manage payouts and review commission approvals.</p>
        </div>
    </div>

    <!-- Stats Review -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
                <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider">Pending Approvals</p>
                <h3 class="text-3xl font-black text-slate-900 mt-1">
                    {{ formatCurrency(transactions.filter(t => t.status === 'Pending').reduce((acc, t) => acc + t.amount, 0)) }}
                </h3>
            </div>
            <div class="w-12 h-12 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center">
                <Clock :size="24" />
            </div>
        </div>
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
             <div>
                <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider">Approved (Unpaid)</p>
                <h3 class="text-3xl font-black text-slate-900 mt-1">
                    {{ formatCurrency(transactions.filter(t => t.status === 'Approved').reduce((acc, t) => acc + t.amount, 0)) }}
                </h3>
            </div>
            <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center">
                <Check :size="24" />
            </div>
        </div>
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
             <div>
                <p class="text-sm font-semibold text-slate-500 uppercase tracking-wider">Total Paid</p>
                <h3 class="text-3xl font-black text-slate-900 mt-1">
                    {{ formatCurrency(transactions.filter(t => t.status === 'Paid').reduce((acc, t) => acc + t.amount, 0)) }}
                </h3>
            </div>
            <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center">
                <DollarSign :size="24" />
            </div>
        </div>
    </div>

    <!-- Transaction List -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden min-h-[400px]">
        <DataTable :value="transactions" :loading="fetchTransactions.loading" paginator :rows="10" class="p-datatable-sm" responsiveLayout="scroll">
            <template #empty>
                <div class="text-center p-12 text-slate-400">No transactions found.</div>
            </template>
            
            <Column field="name" header="TRX ID" style="width: 100px" class="font-mono text-xs text-slate-500" />
            <Column field="date" header="Date" style="width: 120px">
                 <template #body="slotProps">
                    <span class="text-sm text-slate-600">{{ slotProps.data.date }}</span>
                </template>
            </Column>
            <Column field="partner" header="Partner" style="min-width: 150px">
                <template #body="slotProps">
                    <span class="font-bold text-slate-800">{{ slotProps.data.partner }}</span>
                </template>
            </Column>
            <Column field="referral_lead" header="Lead Ref" style="width: 150px">
                <template #body="slotProps">
                    <span class="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">{{ slotProps.data.referral_lead }}</span>
                </template>
            </Column>
            <Column field="amount" header="Amount" style="width: 120px">
                <template #body="slotProps">
                    <span class="font-bold text-slate-900">{{ formatCurrency(slotProps.data.amount) }}</span>
                </template>
            </Column>
            <Column field="status" header="Status" style="width: 120px">
                <template #body="slotProps">
                    <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" class="text-[10px] uppercase font-bold" />
                </template>
            </Column>
            <Column header="Actions" alignFrozen="right" frozen style="width: 140px">
                 <template #body="slotProps">
                     <div class="flex gap-1" v-if="slotProps.data.status === 'Pending'">
                         <Button icon="pi pi-check" size="small" severity="success" rounded text @click="openActionDialog(slotProps.data, 'approve')" v-tooltip="'Approve'" />
                         <Button icon="pi pi-times" size="small" severity="danger" rounded text @click="openActionDialog(slotProps.data, 'reject')" v-tooltip="'Reject'" />
                     </div>
                     <div class="flex gap-1" v-else-if="slotProps.data.status === 'Approved'">
                         <Button icon="pi pi-dollar" size="small" severity="success" rounded outlined @click="openActionDialog(slotProps.data, 'pay')" v-tooltip="'Mark Paid'" />
                     </div>
                 </template>
            </Column>
        </DataTable>
    </div>

    <!-- Action Dialog -->
    <Dialog v-model:visible="actionDialogVisible" :header="actionType === 'approve' ? 'Approve Transaction' : actionType === 'pay' ? 'Mark as Paid' : 'Reject Transaction'" modal class="w-full max-w-md">
        <div class="space-y-4 pt-2">
            <p v-if="actionType === 'approve'" class="text-slate-600">Are you sure you want to approve this commission for <b>{{ selectedTransaction?.partner }}</b>?</p>
            <p v-else-if="actionType === 'pay'" class="text-slate-600">Confirm payment of <b>{{ formatCurrency(selectedTransaction?.amount) }}</b> has been processed offline?</p>
            <p v-else class="text-slate-600">Please provide a reason for rejecting this commission.</p>
            
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-500 uppercase">Note (Optional)</label>
                <Textarea v-model="actionNote" rows="3" class="w-full" placeholder="Add internal note..." />
            </div>
        </div>
        <template #footer>
            <div class="flex justify-end gap-2 pt-4">
                <Button label="Cancel" text @click="actionDialogVisible = false" />
                <Button :label="actionType === 'reject' ? 'Reject' : 'Confirm'" :severity="actionType === 'reject' ? 'danger' : 'success'" @click="submitAction" />
            </div>
        </template>
    </Dialog>
  </div>
</template>
