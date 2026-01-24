<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Mail, MoreHorizontal, Search } from 'lucide-vue-next'
import { createListResource } from 'frappe-ui'

const router = useRouter()

const templates = createListResource({
  doctype: 'Email Template',
  fields: ['name', 'subject', 'response', 'modified'],
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
      <button 
        @click="createNew"
        class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-lg shadow-blue-200 flex items-center gap-2"
      >
        <Plus :size="18" />
        Create Template
      </button>
    </div>

    <!-- Search (Placeholder) -->
    <div class="mb-6">
        <div class="relative max-w-md">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="20" />
            <input 
                type="text" 
                placeholder="Search templates..." 
                class="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
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
            <div class="p-3 bg-indigo-50 text-indigo-600 rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <Mail :size="24" />
            </div>
            <button class="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-50">
                <MoreHorizontal :size="20" />
            </button>
        </div>
        <h3 class="font-bold text-slate-900 mb-1 truncate">{{ template.name }}</h3>
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
        <button 
            @click="createNew"
            class="text-blue-600 font-bold text-sm hover:underline"
        >
            Create New Template
        </button>
    </div>
  </div>
</template>
