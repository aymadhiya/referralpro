<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, 
  Save, 
  Braces,
  ChevronDown
} from 'lucide-vue-next'
import { createResource, createListResource } from 'frappe-ui'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'

const route = useRoute()
const router = useRouter()
const isNew = route.params.id === 'new'
const templateId = route.params.id

const loading = ref(false)
const showVarPicker = ref(false)

const form = ref({
    name: '',
    subject: '',
    response: '' // This is the content
})

// Variable Picker State
const selectedDocType = ref(null)
const selectedField = ref(null)

// Fetch DocTypes for Picker
// We will allow picking from common Agency related doctypes
const doctypes = [
    { label: 'User', value: 'User' },
    { label: 'Organization', value: 'Organization' },
    { label: 'Agreement Template', value: 'Agreement Template' },
]

// Fetch Fields based on DocType
const fieldsResource = createResource({
    url: 'frappe.client.get_list',
    makeParams(values) {
        return {
            doctype: 'DocField',
            filters: { parent: selectedDocType.value },
            fields: ['fieldname', 'label'],
            limit_page_length: 999
        }
    }
})

const insertVariable = () => {
    if (!selectedDocType.value || !selectedField.value) return
    
    // Jinja Syntax: {{ doc.fieldname }} (assuming 'doc' is the context object name usually)
    // Or just fieldname if context is direct
    // Standard Frappe Email Templates use {{ doc.fieldname }} if referencing linked doc, or {{ fieldname }}
    // Let's assume generic {{ doc.fieldname }} for now or {{ fieldname }}
    const variable = `{{ ${selectedField.value} }}`
    
    // Insert into response cursor position (Simple append for now)
    form.value.response += variable
    showVarPicker.value = false
    selectedField.value = null
}

const onDocTypeChange = () => {
    selectedField.value = null
    fieldsResource.submit()
}

// Save Resource
const saveResource = createResource({
    url: 'frappe.client.save',
    makeParams(values) {
        return {
            doc: {
                doctype: 'Email Template',
                name: !isNew ? templateId : form.value.name,
                subject: form.value.subject,
                response: form.value.response,
                // Additional fields if needed
            }
        }
    },
    onSuccess(data) {
        loading.value = false
        if (isNew) {
            router.replace(`/agency/templates/edit/${data.name}`)
        }
    }
})

// Fetch Template
const fetchResource = createResource({
    url: 'frappe.client.get',
    makeParams() {
        return {
            doctype: 'Email Template',
            name: templateId
        }
    },
    onSuccess(data) {
        form.value.name = data.name
        form.value.subject = data.subject
        form.value.response = data.response
    }
})

const handleSave = () => {
    if (!form.value.name || !form.value.subject) {
        alert('Name and Subject are required')
        return
    }
    loading.value = true
    saveResource.submit()
}

onMounted(() => {
    if (!isNew) {
        fetchResource.submit()
    }
})
</script>

<template>
  <div class="h-full flex flex-col bg-slate-50">
    <!-- Header -->
    <header class="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between flex-shrink-0 z-20">
        <div class="flex items-center gap-4">
            <button @click="router.back()" class="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors">
                <ArrowLeft :size="20" />
            </button>
            <div class="flex flex-col">
                <input 
                    v-model="form.name"
                    type="text" 
                    placeholder="Template Name (e.g. Welcome Email)"
                    class="text-lg font-bold text-slate-900 border-none p-0 focus:ring-0 placeholder:text-slate-300 bg-transparent"
                />
            </div>
        </div>
        <button 
            @click="handleSave"
            :disabled="loading"
            class="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 shadow-lg shadow-slate-200 disabled:opacity-50"
        >
            <Save :size="16" />
            {{ loading ? 'Saving...' : 'Save Template' }}
        </button>
    </header>

    <!-- Editor Workspace -->
    <div class="flex-1 overflow-y-auto p-8">
        <div class="max-w-3xl mx-auto space-y-6">
            
            <!-- Subject -->
            <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Subject Line</label>
                <input 
                    v-model="form.subject" 
                    placeholder="Enter email subject..." 
                    class="w-full text-base border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium" 
                />
            </div>

            <!-- Message Body -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col min-h-[500px]">
                
                <!-- Toolbar -->
                <div class="px-4 py-3 border-b border-slate-100 flex items-center gap-2 bg-slate-50/50 rounded-t-2xl">
                    <button 
                        @click="showVarPicker = true"
                        class="flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 hover:border-blue-500 hover:text-blue-600 transition-colors shadow-sm"
                    >
                        <Braces :size="14" />
                        Insert Variable
                    </button>
                </div>

                <!-- Text Area -->
                <textarea 
                    v-model="form.response" 
                    placeholder="Type your email content here..." 
                    class="flex-1 w-full p-6 border-none focus:ring-0 resize-none rounded-b-2xl text-slate-700 leading-relaxed font-mono text-sm"
                ></textarea>
            </div>

        </div>
    </div>

    <!-- Variable Picker Dialog -->
    <Dialog v-model:visible="showVarPicker" modal header="Insert Dynamic Variable" :style="{ width: '25rem' }">
        <div class="flex flex-col gap-4 pt-2">
            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Select DocType</label>
                <Dropdown 
                    v-model="selectedDocType" 
                    :options="doctypes" 
                    optionLabel="label" 
                    optionValue="value" 
                    placeholder="Select a DocType" 
                    class="w-full" 
                    @change="onDocTypeChange"
                />
            </div>
            
            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Select Field</label>
                <Dropdown 
                    v-model="selectedField" 
                    :options="fieldsResource.data || []" 
                    optionLabel="label" 
                    optionValue="fieldname" 
                    placeholder="Select a Field" 
                    class="w-full" 
                    :loading="fieldsResource.loading"
                    :disabled="!selectedDocType"
                />
            </div>

            <div class="flex justify-end pt-4">
                <Button label="Insert" @click="insertVariable" :disabled="!selectedField" />
            </div>
        </div>
    </Dialog>

  </div>
</template>
