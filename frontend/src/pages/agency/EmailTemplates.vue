<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Mail, MoreHorizontal, Search } from 'lucide-vue-next'
import { createListResource } from 'frappe-ui'
import Button from 'primevue/button'

const router = useRouter()

const templates = createListResource({
  doctype: 'Email Template',
  fields: ['name', 'template_name', 'subject', 'response', 'modified'],
  orderBy: 'modified desc'
})

onMounted(() => {
  templates.reload()
})

const createNew = () => {
    router.push('/agency/templates/edit/new')
}

const editTemplate = (id) => {
    router.push(`/agency/templates/edit/${id}`)
}
</script>

<template>
  <div class="p-8 max-w-[1200px] mx-auto">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Email Templates</h1>
        <p class="text-slate-500 mt-1">Manage email templates for automated communications.</p>
      </div>
      <Button 
        @click="createNew"
        label="Create Template"
        icon="pi pi-plus"
        class="shadow-lg"
      />
    </div>

    <!-- Search (Placeholder) -->
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
        class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all group cursor-pointer"
        @click="editTemplate(template.name)"
      >
        <div class="flex justify-between items-start mb-4">
            <div class="p-3 bg-primary-50 text-primary-600 rounded-xl group-hover:bg-primary-600 group-hover:text-white transition-colors">
                <Mail :size="24" />
            </div>
            <Button 
                icon="pi pi-ellipsis-h"
                text
                severity="secondary"
                class="!p-2 hover:bg-surface-50"
            />
        </div>
        <h3 class="font-bold text-slate-900 mb-1 truncate">{{ template.template_name || template.name }}</h3>
        <p class="text-sm text-slate-500 mb-4 truncate">{{ template.subject }}</p>
        
        <p class="text-xs text-slate-400">Last updated {{ template.modified.split(" ")[0] }}</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!templates.loading" class="flex flex-col items-center justify-center min-h-[400px] bg-slate-50/50 rounded-3xl border-2 border-dashed border-slate-200">
        <div class="p-4 bg-white rounded-full shadow-sm mb-4">
            <Mail :size="32" class="text-slate-400" />
        </div>
        <h3 class="text-lg font-bold text-slate-900 mb-1">No templates found</h3>
        <p class="text-slate-500 text-sm mb-6 max-w-xs text-center">Create your first email template to streamline your communication.</p>
        <Button 
            @click="createNew"
            label="Create New Template"
            text
            class="font-bold underline"
        />
    </div>
  </div>
</template>
