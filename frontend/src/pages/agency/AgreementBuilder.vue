<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import draggable from 'vuedraggable'
import { 
  ArrowLeft, 
  Save, 
  Type, 
  AlignLeft, 
  Edit3, 
  Calendar, 
  Trash2,
  GripVertical,
  Plus,
  Eye,
  EyeOff
} from 'lucide-vue-next'
import { createResource } from 'frappe-ui'
import InputText from 'primevue/inputtext'

const route = useRoute()
const router = useRouter()
const isNew = route.params.id === 'new'
const templateId = route.params.id

const loading = ref(false)
const templateName = ref('Untitled Agreement')
const isActive = ref(true)
const previewMode = ref(false)

// Toolbox Items
const toolbox = [
  { type: 'heading', icon: Type, label: 'Heading', properties: { text: 'New Heading', level: 'h2' } },
  { type: 'text', icon: AlignLeft, label: 'Text Block', properties: { content: 'Enter agreement terms here...' } },
  { type: 'input', icon: Edit3, label: 'Input Field', properties: { label: 'Field Label', placeholder: 'Enter value', required: false } },
  { type: 'date', icon: Calendar, label: 'Date Field', properties: { label: 'Date', required: true } },
  // Signature is special, only one usually allowed or specific handling
  { type: 'signature', icon: Edit3, label: 'Signature', properties: { label: 'Client Signature', required: true } },
]

// Canvas Items
const content = ref([])
const selectedBlock = ref(null)

const handleSelect = (index) => {
    if (previewMode.value) return
    selectedBlock.value = index === null ? null : { index, ...content.value[index] }
}

const updateSelectedBlock = () => {
    if (selectedBlock.value !== null) {
        content.value[selectedBlock.value.index] = { 
            ...content.value[selectedBlock.value.index], 
            properties: { ...selectedBlock.value.properties } 
        }
    }
}

const removeBlock = (index) => {
    content.value.splice(index, 1)
    if (selectedBlock.value?.index === index) {
        selectedBlock.value = null
    }
}

// Drag Options
const dragOptions = {
    animation: 200,
    group: "blocks",
    disabled: false,
    ghostClass: "ghost"
}

// Clone logic for toolbox
const cloneBlock = (block) => {
    return {
        id: Math.random().toString(36).substr(2, 9),
        type: block.type,
        properties: { ...block.properties } // Deep copy properties
    }
}

// Resource to Save
const saveResource = createResource({
    url: 'frappe.client.save',
    makeParams(values) {
        return {
            doc: {
                doctype: 'Agreement Template',
                name: !isNew ? templateId : undefined,
                template_name: templateName.value,
                is_active: isActive.value ? 1 : 0,
                content: JSON.stringify(content.value),
                // HARDCODED ORG FOR DEMO (You should get this from user context)
                organization: 'Zenith Marketing' 
            }
        }
    },
    onSuccess(data) {
        loading.value = false
        // Show Toast
        if (isNew) {
            router.replace(`/agency/agreements/builder/${data.name}`)
        }
    }
})

// Fetch Resource
const fetchResource = createResource({
    url: 'frappe.client.get',
    makeParams() {
        return {
            doctype: 'Agreement Template',
            name: templateId
        }
    },
    onSuccess(data) {
        templateName.value = data.template_name
        isActive.value = !!data.is_active
        if (data.content) {
            try {
                content.value = JSON.parse(data.content)
            } catch (e) {
                content.value = []
            }
        }
    }
})

const saveTemplate = () => {
    if (!templateName.value) {
        alert('Please enter a template name')
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

watch(() => selectedBlock.value?.properties, () => {
   updateSelectedBlock() 
}, { deep: true })

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
                    v-model="templateName"
                    type="text" 
                    placeholder="Untitled Agreement"
                    :disabled="previewMode"
                    class="text-lg font-bold text-slate-900 border-none p-0 focus:ring-0 placeholder:text-slate-300 bg-transparent"
                />
                <p v-if="!previewMode" class="text-xs text-slate-500 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" :class="isActive ? 'bg-emerald-500' : 'bg-slate-300'"></span>
                    {{ isActive ? 'Active Template' : 'Draft' }}
                </p>
                 <p v-else class="text-xs text-blue-500 uppercase font-bold tracking-wider">
                    Preview Mode
                </p>
            </div>
        </div>
        <div class="flex items-center gap-3">
             <div v-if="!previewMode" class="flex items-center gap-2 mr-4 bg-slate-100 p-1 rounded-lg">
                <button 
                    @click="isActive = false"
                    class="px-3 py-1.5 text-xs font-semibold rounded-md transition-all"
                    :class="!isActive ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-700'"
                >
                    Draft
                </button>
                 <button 
                    @click="isActive = true"
                    class="px-3 py-1.5 text-xs font-semibold rounded-md transition-all"
                    :class="isActive ? 'bg-white shadow-sm text-emerald-600' : 'text-slate-500 hover:text-slate-700'"
                >
                    Active
                </button>
            </div>
            
            <button 
                @click="previewMode = !previewMode"
                class="px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
                :class="previewMode ? 'bg-blue-50 text-blue-600 hover:bg-blue-100' : 'text-slate-500 hover:bg-slate-100'"
            >
                <component :is="previewMode ? EyeOff : Eye" :size="16" />
                {{ previewMode ? 'Edit Template' : 'Preview' }}
            </button>

            <button 
                v-if="!previewMode"
                @click="saveTemplate"
                :disabled="loading"
                class="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 shadow-lg shadow-slate-200 disabled:opacity-50"
            >
                <Save :size="16" />
                {{ loading ? 'Saving...' : 'Save Template' }}
            </button>
        </div>
    </header>

    <!-- Builder Workspace -->
    <div class="flex-1 flex overflow-hidden">
        
        <!-- Sidebar (Hidden in Preview) -->
        <aside v-if="!previewMode" class="w-72 bg-white border-r border-slate-200 flex flex-col flex-shrink-0 z-10 transition-all">
            <div class="p-4 border-b border-slate-100">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Blocks</h3>
            </div>
            <div class="p-4 flex-1 overflow-y-auto">
                <draggable 
                    :list="toolbox" 
                    :group="{ name: 'blocks', pull: 'clone', put: false }" 
                    :clone="cloneBlock"
                    :sort="false"
                    item-key="type"
                    class="space-y-3"
                >
                    <template #item="{ element }">
                        <div class="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md cursor-grab active:cursor-grabbing transition-all group">
                            <div class="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center text-slate-500 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                                <component :is="element.icon" :size="18" />
                            </div>
                            <span class="text-sm font-medium text-slate-700">{{ element.label }}</span>
                        </div>
                    </template>
                </draggable>
            </div>
            
            <!-- Properties Panel (Contextual) -->
             <div v-if="selectedBlock" class="border-t border-slate-200 flex flex-col h-1/2 bg-slate-50/50">
                 <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-white">
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Properties</h3>
                    <button @click="selectedBlock = null" class="text-slate-400 hover:text-slate-600">
                         &times;
                    </button>
                </div>
                <div class="p-4 space-y-4 overflow-y-auto flex-1">
                    <div v-if="selectedBlock.properties.text !== undefined">
                        <label class="block text-xs font-semibold text-slate-500 mb-1.5">Heading Text</label>
                        <input v-model="selectedBlock.properties.text" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0" />
                    </div>
                     <div v-if="selectedBlock.properties.content !== undefined">
                        <label class="block text-xs font-semibold text-slate-500 mb-1.5">Content</label>
                        <textarea rows="4" v-model="selectedBlock.properties.content" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0"></textarea>
                    </div>
                     <div v-if="selectedBlock.properties.label !== undefined">
                        <label class="block text-xs font-semibold text-slate-500 mb-1.5">Label</label>
                        <input v-model="selectedBlock.properties.label" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0" />
                    </div>
                     <div v-if="selectedBlock.properties.placeholder !== undefined">
                        <label class="block text-xs font-semibold text-slate-500 mb-1.5">Placeholder</label>
                        <input v-model="selectedBlock.properties.placeholder" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0" />
                    </div>
                     <div v-if="selectedBlock.properties.required !== undefined" class="flex items-center gap-2">
                        <input type="checkbox" v-model="selectedBlock.properties.required" id="req_prop" class="rounded border-slate-300 text-blue-600 focus:ring-0" />
                        <label for="req_prop" class="text-sm text-slate-700">Required Field</label>
                    </div>
                </div>
             </div>
        </aside>

        <!-- Canvas -->
        <main class="flex-1 bg-slate-50 p-8 overflow-y-auto transition-all" :class="previewMode ? 'flex justify-center' : ''">
            <div 
                class="max-w-3xl w-full min-h-[800px] bg-white rounded-[2rem] shadow-sm border border-slate-200 p-10 md:p-16 flex flex-col relative group/canvas transition-all"
                :class="previewMode ? 'shadow-2xl border-transparent scale-[1.02]' : ''"
            >
                
                <draggable 
                    :list="content" 
                    group="blocks" 
                    item-key="id"
                    v-bind="{...dragOptions, disabled: previewMode}"
                    class="flex-1 space-y-4 min-h-[200px]"
                >
                     <template #item="{ element, index }">
                        <div 
                            @click.stop="handleSelect(index)"
                            class="relative group/item border-2 border-transparent rounded-xl transition-all"
                            :class="[
                                !previewMode && selectedBlock?.index === index ? 'border-blue-500 bg-blue-50/10' : '',
                                !previewMode ? 'hover:border-slate-200' : ''
                            ]"
                        >
                            <!-- Drag Handle & Actions (Hidden in Preview) -->
                            <div v-if="!previewMode" class="absolute -right-3 -top-3 hidden group-hover/item:flex items-center gap-1 bg-white shadow-md border border-slate-100 rounded-lg p-1 z-10"
                                :class="{ 'flex': selectedBlock?.index === index }"
                            >
                                <div class="cursor-move p-1 text-slate-400 hover:text-slate-600 Handle"><GripVertical :size="14"/></div>
                                <button @click.stop="removeBlock(index)" class="p-1 text-rose-400 hover:text-rose-600"><Trash2 :size="14"/></button>
                            </div>

                            <!-- Block Content Renderers -->
                            
                            <!-- Heading -->
                            <div v-if="element.type === 'heading'" class="p-2">
                                <h1 v-if="element.properties.level === 'h1'" class="text-3xl font-bold text-slate-900">{{ element.properties.text }}</h1>
                                <h2 v-else-if="element.properties.level === 'h2'" class="text-2xl font-bold text-slate-900">{{ element.properties.text }}</h2>
                                <h3 v-else class="text-xl font-bold text-slate-900">{{ element.properties.text }}</h3>
                            </div>

                            <!-- Text -->
                             <div v-else-if="element.type === 'text'" class="p-2">
                                <p class="text-slate-600 leading-relaxed whitespace-pre-wrap">{{ element.properties.content }}</p>
                            </div>

                            <!-- Input -->
                             <div v-else-if="element.type === 'input'" class="p-2">
                                <label class="block text-sm font-semibold text-slate-700 mb-1.5">
                                    {{ element.properties.label }} <span v-if="element.properties.required" class="text-rose-500">*</span>
                                </label>
                                <input 
                                    :placeholder="element.properties.placeholder" 
                                    class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900" 
                                    :class="previewMode ? 'focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 cursor-text' : 'cursor-not-allowed'"
                                    :disabled="!previewMode"
                                />
                            </div>

                            <!-- Date -->
                             <div v-else-if="element.type === 'date'" class="p-2">
                                <label class="block text-sm font-semibold text-slate-700 mb-1.5">
                                    {{ element.properties.label }} <span v-if="element.properties.required" class="text-rose-500">*</span>
                                </label>
                                <div 
                                    class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-400 flex items-center justify-between"
                                    :class="previewMode ? 'cursor-pointer hover:border-blue-500' : ''"
                                >
                                    <span>DD/MM/YYYY</span>
                                    <Calendar :size="16" />
                                </div>
                            </div>
                            
                            <!-- Signature -->
                             <div v-else-if="element.type === 'signature'" class="p-4 bg-blue-50/50 border border-dashed border-blue-200 rounded-lg mt-4">
                                <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-4">
                                     {{ element.properties.label }} <span v-if="element.properties.required" class="text-rose-500">*</span>
                                </p>
                                <div 
                                    class="h-24 bg-white border border-slate-200 rounded-lg flex items-center justify-center text-slate-300 text-sm transition-colors"
                                    :class="previewMode ? 'hover:bg-slate-50 cursor-pointer' : ''"
                                >
                                    {{ previewMode ? 'Click to Sign' : 'Sign Here' }}
                                </div>
                            </div>

                        </div>
                    </template>
                    
                    <template #footer>
                         <div v-if="content.length === 0 && !previewMode" class="h-full flex flex-col items-center justify-center text-slate-400 p-10">
                            <Plus :size="48" class="mb-4 text-slate-200" />
                            <p class="font-medium">Drag blocks from the sidebar to start building</p>
                        </div>
                    </template>
                </draggable>

            </div>
        </main>
    </div>
  </div>
</template>

<style scoped>
.ghost {
    opacity: 0.5;
    background: #eff6ff;
    border: 2px dashed #3b82f6;
}
</style>
