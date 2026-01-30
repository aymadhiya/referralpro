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
import Dropdown from 'primevue/dropdown'
import { Pencil, Trash2, Plus, GripVertical } from 'lucide-vue-next'

const fields = ref([])
const dialogVisible = ref(false)
const saving = ref(false)

const fieldTypes = [
    { label: 'Data (Text)', value: 'Data' },
    { label: 'Number (Int)', value: 'Int' },
    { label: 'Decimal (Float)', value: 'Float' },
    { label: 'Dropdown (Select)', value: 'Select' },
    { label: 'Long Text', value: 'Small Text' },
    { label: 'Date', value: 'Date' }
]

const editingField = ref({
    name: null,
    label: '',
    fieldname: '',
    fieldtype: 'Data',
    options: '',
    is_required: false,
    sequence: 0
})

const fetchFields = createResource({
    url: 'referralpro.api.agency.lead_config.get_custom_fields',
    onSuccess: (data) => {
        fields.value = data || []
    }
})

const openDialog = (field = null) => {
    if (field) {
        editingField.value = { ...field }
    } else {
        editingField.value = {
            name: null,
            label: '',
            fieldname: '',
            fieldtype: 'Data',
            options: '',
            is_required: false,
            sequence: fields.value.length + 1
        }
    }
    dialogVisible.value = true
}

const generateFieldname = () => {
    if (!editingField.value.name && editingField.value.label) {
        editingField.value.fieldname = editingField.value.label
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '_')
            .replace(/_+/g, '_')
            .replace(/^_|_$/g, '')
    }
}

const saveField = async () => {
    if (!editingField.value.label || !editingField.value.fieldname) return
    
    saving.value = true
    try {
        const resource = createResource({
            url: 'referralpro.api.agency.lead_config.save_custom_field',
            params: {
                field_data: editingField.value
            },
            onSuccess: () => {
                dialogVisible.value = false
                fetchFields.reload()
            }
        })
        await resource.submit()
    } finally {
        saving.value = false
    }
}

const confirmDelete = async (data) => {
    if (!confirm("Are you sure you want to delete this field? Data stored in this field for existing leads will not be visible.")) return
    
    const resource = createResource({
        url: 'referralpro.api.agency.lead_config.delete_custom_field',
        params: { name: data.name },
        onSuccess: () => {
            fetchFields.reload()
        }
    })
    await resource.submit()
}

onMounted(() => {
    fetchFields.reload()
})
</script>

<template>
<div class="p-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-8">
        <div>
            <h1 class="text-2xl font-bold text-slate-900">Lead Custom Fields</h1>
            <p class="text-slate-500 mt-1">Define additional data points Partners should provide when referring a lead.</p>
        </div>
        <Button label="Add Field" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <DataTable :value="fields" :loading="fetchFields.loading" responsiveLayout="scroll">
            <template #empty>
                <div class="text-center p-8 text-slate-500">No custom fields defined. Add one to capture more details.</div>
            </template>
            
            <Column field="sequence" header="Order" style="width: 80px">
                 <template #body="slotProps">
                    <span class="font-mono text-slate-400">#{{ slotProps.data.sequence }}</span>
                </template>
            </Column>
            
            <Column field="label" header="Label">
                <template #body="slotProps">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-700">{{ slotProps.data.label }}</span>
                        <span class="text-xs text-slate-400 font-mono">{{ slotProps.data.fieldname }}</span>
                    </div>
                </template>
            </Column>
            
            <Column field="fieldtype" header="Type">
                 <template #body="slotProps">
                    <span class="px-2 py-1 bg-slate-100 text-slate-600 rounded text-[10px] font-bold uppercase tracking-wider">
                        {{ slotProps.data.fieldtype }}
                    </span>
                </template>
            </Column>
            
            <Column field="is_required" header="Required" style="width: 100px">
                <template #body="slotProps">
                   <div v-if="slotProps.data.is_required" class="w-2 h-2 rounded-full bg-blue-500 mx-auto" title="Required"></div>
                   <div v-else class="w-2 h-2 rounded-full bg-slate-200 mx-auto" title="Optional"></div>
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
    <Dialog v-model:visible="dialogVisible" :header="editingField.name ? 'Edit Field' : 'New Custom Field'" modal class="w-full max-w-md">
        <div class="space-y-5 pt-2">
            <div class="space-y-1.5">
                <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Field Label</label>
                <InputText v-model="editingField.label" @blur="generateFieldname" placeholder="e.g. Estimated Budget" class="w-full font-medium" />
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Field ID (Internal)</label>
                    <InputText v-model="editingField.fieldname" placeholder="e.g. estimated_budget" class="w-full font-mono text-sm" />
                </div>
                <div class="space-y-1.5">
                    <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Sort Order</label>
                    <InputNumber v-model="editingField.sequence" :min="0" class="w-full" inputClass="p-2.5 rounded-lg border-slate-300 w-full" />
                </div>
            </div>

            <div class="space-y-1.5">
                <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Field Type</label>
                <Dropdown v-model="editingField.fieldtype" :options="fieldTypes" optionLabel="label" optionValue="value" placeholder="Select Type" class="w-full" />
            </div>

            <div v-if="editingField.fieldtype === 'Select'" class="space-y-1.5">
                <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Options</label>
                <textarea v-model="editingField.options" placeholder="One option per line" class="w-full p-3 rounded-xl border-slate-200 text-sm h-24 focus:ring-primary-500 focus:border-primary-500"></textarea>
            </div>

            <div class="bg-slate-50 rounded-lg p-3 border border-slate-100 flex items-center gap-3">
                <Checkbox v-model="editingField.is_required" :binary="true" inputId="is_required" />
                <label for="is_required" class="text-sm font-semibold text-slate-700 cursor-pointer select-none">Mandatory Field</label>
            </div>
        </div>
        
        <template #footer>
            <div class="flex items-center justify-end gap-2 pt-4">
                <Button label="Cancel" text @click="dialogVisible = false" class="font-semibold" />
                <Button label="Save Field" icon="pi pi-check" @click="saveField" :loading="saving" class="px-6 font-bold" />
            </div>
        </template>
    </Dialog>
</div>
</template>
