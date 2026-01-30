<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, FileText, MoreHorizontal, Search, CheckCircle } from 'lucide-vue-next'
import { createListResource, createResource } from 'frappe-ui'
import Menu from 'primevue/menu'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'

const router = useRouter()
const toast = useToast()

const templates = createListResource({
  doctype: 'Agreement Template',
  fields: ['name', 'template_name', 'modified', 'enabled', 'is_default'],
  orderBy: 'modified desc'
})

const setDefaultResource = createResource({
    url: 'frappe.client.set_value',
    makeParams({ name }) {
        return {
            doctype: 'Agreement Template',
            name: name,
            fieldname: 'is_default',
            value: 1
        }
    },
    onSuccess: () => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Default template updated', life: 3000 })
        templates.reload()
    }
})

const deleteResource = createResource({
    url: 'frappe.client.delete',
    makeParams({ name }) {
        return {
            doctype: 'Agreement Template',
            name: name
        }
    },
    onSuccess: () => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Template deleted', life: 3000 })
        templates.reload()
    }
})

onMounted(() => {
  templates.reload()
})

const createNew = () => {
    router.push('/agency/agreements/builder/new')
}

const editTemplate = (id) => {
    router.push(`/agency/agreements/builder/${id}`)
}

const menu = ref(null)
const selectedTemplate = ref(null)

const items = (template) => [
    {
        label: 'Edit',
        icon: 'pi pi-pencil',
        command: () => editTemplate(template.name)
    },
    {
        label: 'Set as Default',
        icon: 'pi pi-check-circle',
        visible: !template.is_default,
        command: () => setDefaultResource.submit({ name: template.name })
    },
    {
        separator: true
    },
    {
        label: 'Delete',
        icon: 'pi pi-trash',
        class: 'text-red-600',
        command: () => {
             deleteResource.submit({ name: template.name })
        }
    }
];

const toggleMenu = (event, template) => {
    selectedTemplate.value = template
    menu.value.toggle(event)
}
</script>

<template>
  <div class="p-8 max-w-[1200px] mx-auto">
    <Toast />
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Agreement Templates</h1>
        <p class="text-slate-500 mt-1">Manage your contract and agreement templates.</p>
      </div>
      <Button 
        @click="createNew"
        label="Create Template"
        icon="pi pi-plus"
        class="shadow-lg"
      />
    </div>

    <!-- Search & Filters (Placeholder) -->
    <div class="mb-6">
        <div class="relative max-w-md">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="20" />
            <input 
                type="text" 
                placeholder="Search templates..." 
                class="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
            >
        </div>
    </div>

    <!-- Grid -->
    <div v-if="templates.data && templates.data.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="template in templates.data" 
        :key="template.name"
        class="bg-white p-5 rounded-2xl border shadow-sm hover:shadow-md transition-all group cursor-pointer"
        @click="editTemplate(template.name)"
      >
        <div class="flex justify-between items-start mb-4">
            <div class="p-3 bg-primary-50 text-primary-600 rounded-xl group-hover:bg-primary-600 group-hover:text-white transition-colors">
                <FileText :size="24" />
            </div>
            <Button 
                icon="pi pi-ellipsis-h"
                text
                severity="secondary"
                @click.stop="toggleMenu($event, template)"
                class="!p-2 hover:bg-surface-50"
            />
        </div>
        <h3 class="font-bold text-slate-900 mb-1">{{ template.template_name }}</h3>
        <p class="text-xs text-slate-500 mb-4">Last updated {{ template.modified.split(" ")[0] }}</p>
        
        <div class="flex items-center gap-2">
            <span 
                class="px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider"
                :class="template.enabled ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'"
            >
                {{ template.enabled ? 'Active' : 'Draft' }}
            </span>
             <span 
                v-if="template.is_default"
                class="px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-600 flex items-center gap-1"
            >
                <CheckCircle :size="10" />
                Default
            </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!templates.loading" class="flex flex-col items-center justify-center min-h-[400px] bg-slate-50/50 rounded-3xl border-2 border-dashed border-slate-200">
        <div class="p-4 bg-white rounded-full shadow-sm mb-4">
            <FileText :size="32" class="text-slate-400" />
        </div>
        <h3 class="text-lg font-bold text-slate-900 mb-1">No templates found</h3>
        <p class="text-slate-500 text-sm mb-6 max-w-xs text-center">Get started by creating your first agreement template for your partners.</p>
        <Button 
            @click="createNew"
            label="Create New Template"
            text
            class="font-bold underline"
        />
    </div>
    <Menu ref="menu" :model="selectedTemplate ? items(selectedTemplate) : []" :popup="true" />
  </div>
</template>
