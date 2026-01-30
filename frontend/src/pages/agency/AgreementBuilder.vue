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
  Trash2,
  GripVertical,
  Plus,
  Eye,
  EyeOff,
  Bold as LucideBold,
  Italic as LucideItalic,
  Underline as LucideUnderline,
  List,
  ListOrdered
} from 'lucide-vue-next'
import { createResource } from 'frappe-ui'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const route = useRoute()
const router = useRouter()
const isNew = route.params.id === 'new'
const templateId = route.params.id

const loading = ref(false)
const templateName = ref('Untitled Agreement')
const isActive = ref(true)
const previewMode = ref(false)

// Color options for text/table
const colors = [
    { label: 'Default', value: 'inherit' },
    { label: 'Gray', value: '#64748b' },
    { label: 'Blue', value: '#3b82f6' },
    { label: 'Emerald', value: '#10b981' },
    { label: 'Rose', value: '#f43f5e' }
]

// Toolbox Items
const toolbox = [
  { 
    type: 'heading', 
    icon: Type, 
    label: 'Heading', 
    properties: { text: 'New Heading', level: 'h2', align: 'left' } 
  },
  { 
    type: 'text', 
    icon: AlignLeft, 
    label: 'Text Block', 
    properties: { content: 'Enter agreement terms here...', align: 'left' } 
  },
  { 
    type: 'table', 
    icon: Plus, 
    label: 'Table', 
    properties: { 
        rows: [['Cell 1', 'Cell 2'], ['Cell 3', 'Cell 4']],
        hasHeader: true,
        striped: false
    } 
  },
  { 
    type: 'signature', 
    icon: Edit3, 
    label: 'Signature', 
    properties: { label: 'Director Signature', required: true } 
  },
]

// Canvas Items
const content = ref([])
const isDefault = ref(false)
const selectedBlock = ref(null)

const handleSelect = (index) => {
    if (previewMode.value) return
    selectedBlock.value = index === null ? null : content.value[index]
    // We link the selectedBlock to the actual content object so changes in sidebar reflect instantly
}

const removeBlock = (index) => {
    content.value.splice(index, 1)
    if (selectedBlock.value === content.value[index]) {
        selectedBlock.value = null
    }
}

// Table Handlers
const addRow = () => {
    if (selectedBlock.value?.type === 'table') {
        const colCount = selectedBlock.value.properties.rows[0].length
        selectedBlock.value.properties.rows.push(new Array(colCount).fill(''))
    }
}

const addColumn = () => {
    if (selectedBlock.value?.type === 'table') {
        selectedBlock.value.properties.rows.forEach(row => row.push(''))
    }
}

const removeRow = (idx) => {
    if (selectedBlock.value?.type === 'table' && selectedBlock.value.properties.rows.length > 1) {
        selectedBlock.value.properties.rows.splice(idx, 1)
    }
}

const removeColumn = (idx) => {
    if (selectedBlock.value?.type === 'table' && selectedBlock.value.properties.rows[0].length > 1) {
        selectedBlock.value.properties.rows.forEach(row => row.splice(idx, 1))
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
        properties: JSON.parse(JSON.stringify(block.properties)) // Deep copy properties
    }
}

const userOrgResource = createResource({
    url: 'referralpro.api.agency.get_current_user_org',
    auto: true
})

// Rich Text Styling Logic
const applyStyle = (command, value = null) => {
    if (!selectedBlock.value) return
    
    document.execCommand(command, false, value)
    
    // After styling, we must sync the DOM changes back to the model immediately
    const activeEl = document.activeElement
    if (activeEl && activeEl.getAttribute('contenteditable') === 'true') {
        const field = selectedBlock.value.type === 'heading' ? 'text' : 'content'
        if (selectedBlock.value.properties[field] !== undefined) {
            selectedBlock.value.properties[field] = activeEl.innerHTML
        }
    }
}

// HTML Generator
const generateHtml = (blocks) => {
    let html = '<div class="print-format">'
    
    blocks.forEach(block => {
        const p = block.properties
        const style = `
            text-align: ${p.align || 'left'};
            font-weight: ${p.bold ? 'bold' : 'normal'};
            font-style: ${p.italic ? 'italic' : 'normal'};
            text-decoration: ${p.underline ? 'underline' : 'none'};
            color: ${p.color || 'inherit'};
        `.replace(/\s+/g, ' ')

        switch(block.type) {
            case 'heading':
                const level = p.level || 'h2'
                html += `
                    <div class="section-break">
                        <div class="section-head">
                            <${level} style="${style}">${p.text || ''}</${level}>
                        </div>
                    </div>`
                break
            case 'text':
                html += `
                    <div class="section-break">
                        <div class="print-format" style="${style}">
                            ${p.content || ''}
                        </div>
                    </div>`
                break
            case 'table':
                html += `<div class="section-break">`
                html += `<table class="table table-bordered" style="width: 100%;">`
                p.rows.forEach((row, rIdx) => {
                    html += `<tr>`
                    row.forEach(cell => {
                        const cellTag = (p.hasHeader && rIdx === 0) ? 'th' : 'td'
                        html += `<${cellTag}>${cell}</${cellTag}>`
                    })
                    html += `</tr>`
                })
                html += `</table></div>`
                break
            case 'signature':
                html += `<div class="signature_required"><div class="section-break">
                    <div class="section-head" style="border-bottom: 2px solid #333; padding-bottom: 5px; font-weight: bold;">${p.label || 'Signature'} ${p.required ? '<span style="color: #e11d48">*</span>' : ''}</div>
                    <div class="row" style="display: flex; flex-wrap: wrap; margin-top: 15px;">
                         <div class="col-xs-6" style="width: 50%;">
                            <div class="field-label" style="font-size: 11px; color: #777; font-weight: bold; text-transform: uppercase;">Signed By</div>
                            <div class="field-value" style="min-height: 40px; border-bottom: 1px solid #eee;"></div>
                         </div>
                         <div class="col-xs-6" style="width: 50%;">
                            <div class="field-label" style="font-size: 11px; color: #777; font-weight: bold; text-transform: uppercase;">Sign Date</div>
                            <div class="field-value" style="min-height: 40px; border-bottom: 1px solid #eee;"></div>
                         </div>
                    </div>
                </div></div>`
                break
        }
    })
    
    html += '</div>'
    return html
}

const modified = ref(null)
const creation = ref(null)
const owner = ref(null)

// Resource to Save
const saveResource = createResource({
    url: 'frappe.client.save',
    makeParams(values) {
        return {
            doc: {
                doctype: 'Agreement Template',
                name: !isNew ? templateId : undefined,
                template_name: templateName.value,
                enabled: isActive.value ? 1 : 0,
                content: JSON.stringify(content.value),
                html_content: generateHtml(content.value),
                organization: userOrgResource.data?.name,
                modified: !isNew ? modified.value : undefined,
                creation: !isNew ? creation.value : undefined,
                owner: !isNew ? owner.value : undefined,
                is_default: isDefault.value ? 1 : 0
            }
        }
    },
    onSuccess(data) {
        loading.value = false       
        modified.value = data.modified // Update timestamp
        creation.value = data.creation
        owner.value = data.owner
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
        isActive.value = !!data.enabled
        modified.value = data.modified
        creation.value = data.creation
        owner.value = data.owner
        isDefault.value = data.is_default


        if (data.content) {
            try {
                content.value = JSON.parse(data.content)
            } catch (e) {
                content.value = []
            }
        }
    }
})

// Update fetch success
fetchResource.transform = (data) => {
    return data
}

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


</script>

<template>
  <div class="h-full flex flex-col bg-slate-50">
    <!-- Header -->
    <header class="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between flex-shrink-0 z-20">
        <div class="flex items-center gap-4">
            <Button 
                icon="pi pi-arrow-left"
                text
                severity="secondary"
                @click="router.back()"
                class="!p-2 text-slate-500"
            />
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
                <Button 
                    label="Draft"
                    text
                    @click="isActive = false"
                    class="!px-3 !py-1.5 !text-xs font-semibold !rounded-md"
                    :severity="!isActive ? 'secondary' : 'secondary'"
                    :class="[!isActive ? '!bg-white shadow-sm !text-slate-900' : '!text-slate-500 hover:!text-slate-700']"
                />
                 <Button 
                    label="Active"
                    text
                    @click="isActive = true"
                    class="!px-3 !py-1.5 !text-xs font-semibold !rounded-md"
                    :severity="isActive ? 'success' : 'secondary'"
                    :class="[isActive ? '!bg-white shadow-sm !text-emerald-600' : '!text-slate-500 hover:!text-slate-700']"
                />
            </div>
            
            <Button 
                @click="previewMode = !previewMode"
                :label="previewMode ? 'Edit Template' : 'Preview'"
                :icon="previewMode ? 'pi pi-eye-slash' : 'pi pi-eye'"
                text
                :severity="previewMode ? 'info' : 'secondary'"
                class="!px-4 !py-2 !text-sm font-semibold"
            />

            <Button 
                v-if="!previewMode"
                @click="saveTemplate"
                :loading="loading"
                :label="loading ? 'Saving...' : 'Save Template'"
                icon="pi pi-save"
                class="px-4 !py-2 !text-sm font-semibold !shadow-lg"
            />
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
                    class="flex-1 space-y-4 min-h-[500px]"
                >
                     <template #item="{ element, index }">
                        <div 
                            @click.stop="handleSelect(index)"
                            class="relative group/item border border-transparent rounded-xl transition-all p-4"
                            :class="[
                                !previewMode && selectedBlock === content[index] ? 'selected-block border-blue-200' : 'hover:border-slate-100'
                            ]"
                        >
                            <!-- Drag Handle & Actions -->
                            <div v-if="!previewMode" class="absolute -right-3 -top-3 hidden group-hover/item:flex items-center gap-1 bg-white shadow-md border border-slate-100 rounded-lg p-1 z-10"
                                :class="{ 'flex': selectedBlock === content[index] }"
                            >
                                <div class="cursor-move p-1 text-slate-400 hover:text-slate-600 Handle"><GripVertical :size="14"/></div>
                                <Button 
                                    icon="pi pi-trash"
                                    text
                                    rounded
                                    severity="danger"
                                    @click.stop="removeBlock(index)"
                                    class="!p-1 !w-6 !h-6"
                                />
                            </div>

                            <!-- HYBRID Block Renderers -->
                            
                            <!-- Heading Edit -->
                            <div v-if="element.type === 'heading'" :style="{ textAlign: element.properties.align || 'left' }">
                                <div 
                                    contenteditable="true"
                                    class="w-full bg-transparent border-none p-0 focus:ring-0 outline-none empty:before:content-[attr(placeholder)] empty:before:text-slate-200"
                                    :placeholder="'Heading ' + (element.properties.level === 'h1' ? '1' : element.properties.level === 'h2' ? '2' : '3')"
                                    :class="{
                                        'text-3xl font-bold': element.properties.level === 'h1',
                                        'text-2xl font-bold': element.properties.level === 'h2',
                                        'text-xl font-bold': element.properties.level === 'h3'
                                    }"
                                    :style="{
                                        color: element.properties.color || 'inherit'
                                    }"
                                    @focus="handleSelect(index)"
                                    @blur="e => element.properties.text = e.target.innerHTML"
                                    v-html="element.properties.text"
                                    v-if="!previewMode"
                                ></div>
                                <div v-else 
                                    class="font-bold"
                                    :class="{
                                        'text-3xl': element.properties.level === 'h1',
                                        'text-2xl': element.properties.level === 'h2',
                                        'text-xl': element.properties.level === 'h3'
                                    }"
                                    :style="{ textAlign: element.properties.align || 'left', color: element.properties.color || 'inherit' }"
                                    v-html="element.properties.text"
                                ></div>
                            </div>

                            <!-- Text Edit (HYBRID RICHTEXT) -->
                             <div v-else-if="element.type === 'text'" :style="{ textAlign: element.properties.align || 'left' }">
                                <div
                                    contenteditable="true"
                                    class="w-full bg-transparent border-none p-0 focus:ring-0 text-slate-700 leading-relaxed outline-none min-h-[1.5em] empty:before:content-[attr(placeholder)] empty:before:text-slate-300"
                                    placeholder="Enter agreement text..."
                                    :style="{ color: element.properties.color || 'inherit' }"
                                    @focus="handleSelect(index)"
                                    @blur="e => element.properties.content = e.target.innerHTML"
                                    v-html="element.properties.content"
                                    v-if="!previewMode"
                                ></div>
                                <div v-else class="text-slate-700 leading-relaxed" v-html="element.properties.content" :style="{ color: element.properties.color || 'inherit' }"></div>
                            </div>

                            <!-- Table Edit (RICHTEXT CELLS) -->
                            <div v-else-if="element.type === 'table'" class="overflow-x-auto">
                                <table class="builder-table w-full border-collapse">
                                    <tr v-for="(row, rIdx) in element.properties.rows" :key="rIdx">
                                        <template v-for="(cell, cIdx) in row" :key="cIdx">
                                            <th v-if="element.properties.hasHeader && rIdx === 0" class="border border-slate-300 bg-slate-50 p-0 text-left">
                                                 <div 
                                                    contenteditable="true"
                                                    class="w-full bg-transparent border-none p-2 focus:ring-1 focus:ring-blue-400 font-bold text-sm text-slate-800 outline-none"
                                                    @focus="handleSelect(index)"
                                                    @blur="e => element.properties.rows[rIdx][cIdx] = e.target.innerHTML"
                                                    v-html="element.properties.rows[rIdx][cIdx]"
                                                    v-if="!previewMode"
                                                ></div>
                                                <div v-else class="p-2 font-bold text-sm text-slate-800" v-html="element.properties.rows[rIdx][cIdx]"></div>
                                            </th>
                                            <td v-else class="border border-slate-300 p-0">
                                                <div 
                                                    contenteditable="true"
                                                    class="w-full bg-transparent border-none p-2 focus:ring-1 focus:ring-blue-400 text-sm text-slate-600 outline-none"
                                                    @focus="handleSelect(index)"
                                                    @blur="e => element.properties.rows[rIdx][cIdx] = e.target.innerHTML"
                                                    v-html="element.properties.rows[rIdx][cIdx]"
                                                    v-if="!previewMode"
                                                ></div>
                                                <div v-else class="p-2 text-sm text-slate-600" v-html="element.properties.rows[rIdx][cIdx]"></div>
                                            </td>
                                        </template>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Signature -->
                             <div v-else-if="element.type === 'signature'" class="p-6 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl transition-all">
                                <div class="mb-4 flex items-center justify-between">
                                    <div class="flex items-center gap-2">
                                        <div class="w-2 h-6 bg-blue-500 rounded-full"></div>
                                        <span class="text-xs font-black text-slate-800 uppercase tracking-widest">{{ element.properties.label || 'SIGNATURE' }}</span>
                                        <span v-if="element.properties.required" class="text-rose-500 font-bold">*</span>
                                    </div>
                                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Required Field</div>
                                </div>
                                <div class="h-24 bg-white border border-slate-200 rounded-xl flex items-center justify-center text-slate-300 text-sm italic">
                                    Sign Here
                                </div>
                            </div>

                        </div>
                    </template>
                    
                    <template #footer>
                         <div v-if="content.length === 0 && !previewMode" class="h-full flex flex-col items-center justify-center text-slate-400 p-20 border-2 border-dashed border-slate-200 rounded-[2.5rem] bg-white">
                            <Plus :size="48" class="mb-4 text-slate-300" />
                            <h4 class="text-lg font-bold text-slate-900 mb-1">Start Building</h4>
                            <p class="text-sm">Drag elements from the left toolbox onto this page</p>
                        </div>
                    </template>
                </draggable>

            </div>
        </main>

        <!-- Right Sidebar (STYLING & PROPERTIES) -->
        <aside v-if="selectedBlock && !previewMode" class="w-80 bg-white border-l border-slate-200 flex flex-col flex-shrink-0 z-10 transition-all shadow-xl">
             <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <div class="flex items-center gap-2">
                    <Edit3 :size="14" class="text-blue-500" />
                    <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Styling: {{ selectedBlock.type }}</h3>
                </div>
                <Button 
                    icon="pi pi-times"
                    text
                    severity="secondary"
                    @click="selectedBlock = null"
                    class="!p-1"
                />
            </div>
            
            <div class="p-6 space-y-6 overflow-y-auto flex-1">
                
                <!-- HEADING STYLING -->
                <template v-if="selectedBlock.type === 'heading'">
                    <div class="space-y-4">
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Heading Level</label>
                                <select v-model="selectedBlock.properties.level" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0 bg-slate-50">
                                    <option value="h1">Large (H1)</option>
                                    <option value="h2">Medium (H2)</option>
                                    <option value="h3">Small (H3)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Alignment</label>
                                <select v-model="selectedBlock.properties.align" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0 bg-slate-50">
                                    <option value="left">Left</option>
                                    <option value="center">Center</option>
                                    <option value="right">Right</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="pt-4 border-t border-slate-100">
                             <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3">Heading Styling</label>
                              <div class="flex gap-2">
                                <Button 
                                    icon="pi pi-bold"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('bold')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-italic"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('italic')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-underline"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('underline')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <select 
                                    @change="e => applyStyle('foreColor', e.target.value)"
                                    class="flex-1 text-xs border-slate-200 rounded-lg focus:ring-0 bg-slate-50 ml-2"
                                >
                                    <option v-for="c in colors" :key="c.value" :value="c.value">{{ c.label }}</option>
                                </select>
                             </div>
                        </div>
                    </div>
                </template>

                <!-- TEXT STYLING -->
                <template v-else-if="selectedBlock.type === 'text'">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Text Alignment</label>
                            <select v-model="selectedBlock.properties.align" class="w-full text-sm border-slate-200 rounded-lg focus:border-blue-500 focus:ring-0 bg-slate-50">
                                <option value="left">Left</option>
                                <option value="center">Center</option>
                                <option value="right">Right</option>
                                <option value="justify">Justify</option>
                            </select>
                        </div>

                         <div class="pt-4 border-t border-slate-100">
                             <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3">Rich Text Styling</label>
                              <div class="flex gap-2">
                                <Button 
                                    icon="pi pi-bold"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('bold')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-italic"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('italic')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-underline"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('underline')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-list"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('insertUnorderedList')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-list-numbered"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('insertOrderedList')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <select 
                                    @change="e => applyStyle('foreColor', e.target.value)"
                                    class="flex-1 text-xs border-slate-200 rounded-lg focus:ring-0 bg-slate-50 ml-2"
                                >
                                    <option v-for="c in colors" :key="'text-c-'+c.value" :value="c.value">{{ c.label }}</option>
                                </select>
                             </div>
                        </div>
                    </div>
                </template>

                <!-- TABLE STRUCTURE -->
                <template v-else-if="selectedBlock.type === 'table'">
                    <div class="space-y-4">
                         <div>
                             <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3">Table Actions</label>
                             <div class="grid grid-cols-2 gap-3">
                                <Button 
                                    @click="addColumn"
                                    label="Add Column"
                                    icon="pi pi-plus"
                                    text
                                    severity="info"
                                    class="!text-[11px] !bg-blue-50 !px-3 !py-2 !rounded-lg font-bold border !border-blue-100"
                                />
                                <Button 
                                    @click="addRow"
                                    label="Add Row"
                                    icon="pi pi-plus"
                                    text
                                    severity="success"
                                    class="!text-[11px] !bg-emerald-50 !px-3 !py-2 !rounded-lg font-bold border !border-emerald-100"
                                />
                             </div>
                         </div>
                         
                         <div class="flex items-center gap-4 py-4 border-y border-slate-100">
                             <div class="flex items-center gap-2">
                                <input type="checkbox" v-model="selectedBlock.properties.hasHeader" id="table_header" class="rounded border-slate-300 text-blue-600 focus:ring-0" />
                                <label for="table_header" class="text-xs text-slate-700 font-bold">Show Header Row</label>
                             </div>
                         </div>

                         <!-- Table Styling Buttons (apply to active cell selection) -->
                         <div class="pt-2 border-b border-slate-100 pb-4">
                             <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-3">Cell Styling</label>
                             <div class="flex gap-2">
                                <Button 
                                    icon="pi pi-bold"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('bold')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-italic"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('italic')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                                <Button 
                                    icon="pi pi-underline"
                                    text
                                    severity="secondary"
                                    @mousedown.prevent="applyStyle('underline')"
                                    class="!w-8 !h-8 !border !border-slate-200 !text-slate-400 hover:!border-blue-300 hover:!text-blue-600"
                                />
                             </div>
                         </div>

                         <div class="pt-2">
                             <label class="block text-[10px] font-bold text-slate-300 uppercase tracking-wide mb-2">Column Cleanup</label>
                             <div class="flex flex-wrap gap-2">
                                <Button
                                    v-for="(col, cIdx) in selectedBlock.properties.rows[0]"
                                    :key="'del-col-'+cIdx"
                                    :label="'Remove Col ' + (cIdx + 1)"
                                    text
                                    severity="danger"
                                    @click="removeColumn(cIdx)"
                                    class="!text-[9px] !bg-slate-50 !px-2 !py-1 !rounded border !border-slate-200 hover:!text-red-500 hover:!border-red-200"
                                    v-if="selectedBlock.properties.rows[0].length > 1"
                                />
                             </div>
                         </div>
                    </div>
                </template>

                <!-- SIGNATURE PROPERTIES -->
                <template v-else-if="selectedBlock.type === 'signature'">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Signatory Label</label>
                            <InputText v-model="selectedBlock.properties.label" class="w-full !text-slate-900 !bg-slate-50" placeholder="e.g. Authorized Director" />
                        </div>
                        <div class="flex items-center gap-2 pt-4 border-t border-slate-100">
                             <input type="checkbox" v-model="selectedBlock.properties.required" id="sig_req" class="rounded border-slate-300 text-blue-600 focus:ring-0" />
                             <label for="sig_req" class="text-xs text-slate-700 font-bold">This signature is required</label>
                        </div>
                    </div>
                </template>

                <div class="pt-8 border-t border-slate-100 mt-auto">
                    <Button 
                        @click="removeBlock(content.indexOf(selectedBlock))"
                        label="Delete This Block"
                        icon="pi pi-trash"
                        severity="danger"
                        outlined
                        class="w-full !py-3 !text-xs font-black uppercase tracking-widest"
                    />
                    <p class="text-[9px] text-slate-300 text-center mt-4 font-bold uppercase tracking-tighter">Click anywhere on page to deselect</p>
                </div>
            </div>
        </aside>
    </div>
  </div>
</template>

<style scoped>
.ghost {
    opacity: 0.5;
    background: #eff6ff;
    border: 2px dashed #3b82f6;
}


.preview-table th, .preview-table td {
    border: 1px solid #e2e8f0;
    padding: 10px;
}

.preview-table th {
    background-color: #f8fafc;
    color: #475569;
}

:deep(.p-inputtext) {
    border-radius: 8px;
    font-size: 14px;
    color: #334155;
}

:deep(.p-inputtext:focus) {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px #dbeafe;
}

/* List Styles */
:deep(ul) {
    list-style-type: disc;
    margin-left: 1.5rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
:deep(ol) {
    list-style-type: decimal;
    margin-left: 1.5rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
:deep(li) {
    margin-bottom: 0.25rem;
}
</style>
