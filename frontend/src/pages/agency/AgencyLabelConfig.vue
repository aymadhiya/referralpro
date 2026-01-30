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
import ColorPicker from 'primevue/colorpicker'
import { Pencil, Trash2, Plus } from 'lucide-vue-next'
import { useToast } from "primevue/usetoast"

// Since we might not have Toast configured globally or in layout, using simple alert or locally checking usage
// Assuming standard PrimeVue usage.

const statuses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const deleteLoading = ref(false)

const editingStatus = ref({
    name: null,
    label: '',
    color: '3b82f6', // default blue without #
    sequence: 0,
    is_final: false
})

const fetchStatuses = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Lead Status',
        fields: JSON.stringify(['name', 'label', 'color', 'sequence', 'is_final']),
        order_by: 'sequence asc'
    },
    onSuccess: (data) => {
        statuses.value = data || []
    }
})

const openDialog = (status = null) => {
    if (status) {
        editingStatus.value = { 
            ...status, 
            color: status.color ? status.color.replace('#', '') : '3b82f6',
            is_final: !!status.is_final
        }
    } else {
        editingStatus.value = {
            name: null,
            label: '',
            color: '3b82f6',
            sequence: statuses.value.length + 1,
            is_final: false
        }
    }
    dialogVisible.value = true
}

const saveStatus = async () => {
    saving.value = true
    try {
        const payload = {
            name: editingStatus.value.name,
            label: editingStatus.value.label,
            color: '#' + editingStatus.value.color,
            sequence: editingStatus.value.sequence,
            is_final: editingStatus.value.is_final
        }

        const data = createResource({
            method: 'post',
            url: 'referralpro.api.agency.doc.save_doc',
            params: {
                doctype: 'Lead Status',
                doc: payload
            },
            onSuccess: () => {
                dialogVisible.value = false
                fetchStatuses.reload()
            }
        })
        await data.reload()
    } finally {
        saving.value = false
    }
}

const confirmDelete = async (data) => {
    if(!confirm("Are you sure you want to delete this status?")) return;
    
    const resource = createResource({
        method: 'post',
        url: 'referralpro.api.agency.doc.delete_doc',
        params: { 
            doctype: 'Lead Status',
            name: data.name 
        },
        onSuccess: () => {
            fetchStatuses.reload()
        }
    })
    await resource.reload()
}

onMounted(() => {
    fetchStatuses.reload()
})

</script>

<template>
<div class="p-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-8">
        <div>
            <h1 class="text-2xl font-bold text-slate-900">Lead Status</h1>
            <p class="text-slate-500 mt-1">Manage the lifecycle stages for your referrals.</p>
        </div>
        <Button 
            label="Add Status" 
            icon="pi pi-plus" 
            @click="openDialog()" 
        />
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <DataTable :value="statuses" :loading="fetchStatuses.loading" responsiveLayout="scroll">
            <template #empty>
                <div class="text-center p-8 text-slate-500">No statuses found. Add one to get started.</div>
            </template>
            
            <Column field="sequence" header="Order" style="width: 100px">
                 <template #body="slotProps">
                    <span class="font-mono text-slate-500">#{{ slotProps.data.sequence }}</span>
                </template>
            </Column>
            
            <Column field="label" header="Label">
                <template #body="slotProps">
                    <span class="font-semibold text-slate-700">{{ slotProps.data.label }}</span>
                </template>
            </Column>
            
            <Column field="color" header="Color">
                 <template #body="slotProps">
                    <div class="flex items-center gap-2">
                        <div class="w-6 h-6 rounded-md shadow-sm border border-slate-100" :style="{ backgroundColor: slotProps.data.color }"></div>
                        <span class="text-xs text-slate-500 uppercase">{{ slotProps.data.color }}</span>
                    </div>
                </template>
            </Column>
            
            <Column field="is_final" header="Is Final">
                <template #body="slotProps">
                   <span v-if="slotProps.data.is_final" class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold">Yes</span>
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
                            @click="openDialog(slotProps.data)"
                            class="!p-2"
                        />
                        <Button 
                            icon="pi pi-trash"
                            text
                            rounded
                            severity="danger"
                            @click="confirmDelete(slotProps.data)"
                            class="!p-2"
                        />
                    </div>
                </template>
            </Column>
        </DataTable>
    </div>

    <!-- Edit/Add Dialog -->
    <Dialog v-model:visible="dialogVisible" :header="editingStatus.name ? 'Edit Status' : 'New Status'" modal class="w-full max-w-md" :pt="{ root: { class: 'bg-white rounded-xl' } }">
        <div class="space-y-5 pt-2">
            <div class="space-y-1.5">
                <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Label</label>
                <InputText v-model="editingStatus.label" autofocus placeholder="e.g. Lead, Negotiating" class="w-full font-medium" />
            </div>
            
            <div class="space-y-4">
                 <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Sort Order</label>
                    <InputNumber v-model="editingStatus.sequence" :min="0" class="w-full" inputClass="font-medium p-3 rounded-lg border-slate-300" placeholder="0" />
                </div>
                 <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Color Code</label>
                    <div class="flex items-center gap-3">
                         <div class="p-1 rounded-lg border border-slate-200 bg-white shadow-sm">
                            <ColorPicker v-model="editingStatus.color" />
                         </div>
                         <div class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 flex items-center gap-2">
                             <span class="text-slate-400 font-medium">#</span>
                             <InputText v-model="editingStatus.color" class="flex-1 bg-transparent border-none p-0 focus:shadow-none text-slate-700 font-mono font-medium" :maxlength="6" />
                         </div>
                    </div>
                </div>
            </div>
            
            <div class="bg-slate-50 rounded-lg p-3 border border-slate-100 mt-2">
                <div class="flex items-center gap-2">
                    <Checkbox v-model="editingStatus.is_final" :binary="true" inputId="is_final" />
                    <label for="is_final" class="text-sm font-semibold text-slate-700 cursor-pointer select-none">Mark as Final Stage</label>
                </div>
                <p class="text-xs text-slate-500 pl-8 mt-1">Enable if this status ends the referral workflow (e.g. Won/Lost).</p>
            </div>
        </div>
        
        <template #footer>
            <div class="flex items-center justify-end gap-2 pt-4">
                <Button label="Cancel" text @click="dialogVisible = false" class="font-semibold" />
                <Button label="Save" @click="saveStatus" :loading="saving" class="px-6 font-bold" />
            </div>
        </template>
    </Dialog>
</div>
</template>

<style scoped>
:deep(.p-colorpicker-preview) {
    width: 2rem;
    height: 2rem;
    border-radius: 0.5rem;
}
:deep(.p-datatable-header) {
    background: transparent;
    border: none;
}
</style>
