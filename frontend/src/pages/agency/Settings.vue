<template>
  <div class="p-6 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Settings</h1>
        <p class="text-surface-500 dark:text-surface-400 mt-1">Manage your organization's branding and preferences.</p>
      </div>
      <Button 
        label="Save Changes" 
        icon="pi pi-check" 
        @click="saveSettings" 
        :loading="saving"
        class="font-bold px-6" 
      />
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
        <i class="pi pi-spin pi-spinner text-4xl text-slate-300"></i>
    </div>

    <div v-else class="space-y-6">
        <!-- Branding Section -->
        <div class="rounded-xl shadow-sm border border-surface-200 dark:border-surface-700 overflow-hidden">
             <div class="p-6 border-b border-surface-100 dark:border-surface-700">
                <h2 class="text-lg font-bold text-surface-900 dark:text-surface-0">Branding</h2>
                <p class="text-sm text-surface-500 dark:text-surface-400 mt-1">Customize how your agency looks to partners.</p>
             </div>
             
             <div class="p-6 space-y-6">
                 <!-- Logo & Favicon Grid -->
                 <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                     <!-- Logo -->
                     <div class="space-y-3">
                         <label class="text-xs font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider">Logo</label>
                         <div class="flex items-start gap-4">
                             <div class="w-24 h-24 rounded-lg border-2 border-dashed border-surface-300 dark:border-surface-600 flex items-center justify-center bg-surface-50 overflow-hidden relative group">
                                 <img v-if="settings.logo" :src="settings.logo" class="w-full h-full object-contain p-2" />
                                  <div v-if="!settings.logo" class="text-surface-400 dark:text-surface-500 flex flex-col items-center">
                                     <i class="pi pi-image text-2xl mb-1"></i>
                                     <span class="text-[10px] font-medium">No Logo</span>
                                  </div>
                             </div>
                             
                             <div class="flex-1 space-y-2">
                                <FileUpload 
                                    mode="basic" 
                                    name="file" 
                                    accept="image/*" 
                                    :maxFileSize="2000000" 
                                    customUpload 
                                    @uploader="(e) => customUploader(e, 'logo')" 
                                    auto 
                                    :chooseLabel="settings.logo ? 'Change Logo' : 'Upload Logo'"
                                    class="w-full"
                                    :pt="{
                                        chooseButton: { class: 'w-full p-button-outlined p-button-secondary p-button-sm justify-center' }
                                    }"
                                />
                                <div v-if="settings.logo" class="flex justify-end">
                                    <Button 
                                        label="Remove Logo"
                                        icon="pi pi-trash"
                                        severity="danger"
                                        text
                                        class="!text-xs font-medium"
                                        @click="settings.logo = null"
                                    />
                                </div>
                                <p class="text-xs text-surface-400">Recommended size: 512x512px. Max 2MB. PNG or JPG.</p>
                             </div>
                         </div>
                     </div>



                     <!-- Favicon -->
                     <div class="space-y-3">
                         <label class="text-xs font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider">Favicon</label>
                         <div class="flex items-start gap-4">
                             <div class="w-16 h-16 rounded-lg border-2 border-dashed border-surface-300 dark:border-surface-600 flex items-center justify-center bg-surface-50 overflow-hidden relative group">
                                 <img v-if="settings.favicon" :src="settings.favicon" class="w-full h-full object-contain p-2" />
                                  <div v-if="!settings.favicon" class="text-surface-400 dark:text-surface-500 flex flex-col items-center">
                                     <i class="pi pi-star text-xl mb-1"></i>
                                     <span class="text-[10px] font-medium">None</span>
                                  </div>
                             </div>
                             
                             <div class="flex-1 space-y-2">
                                <FileUpload 
                                    mode="basic" 
                                    name="file" 
                                    accept="image/*" 
                                    :maxFileSize="2000000" 
                                    customUpload 
                                    @uploader="(e) => customUploader(e, 'favicon')" 
                                    auto 
                                    :chooseLabel="settings.favicon ? 'Change Favicon' : 'Upload Favicon'"
                                    class="w-full"
                                    :pt="{
                                        chooseButton: { class: 'w-full p-button-outlined p-button-secondary p-button-sm justify-center' }
                                    }"
                                />
                                <div v-if="settings.favicon" class="flex justify-end">
                                    <Button 
                                        label="Remove Favicon"
                                        icon="pi pi-trash"
                                        severity="danger"
                                        text
                                        class="!text-xs font-medium"
                                        @click="settings.favicon = null"
                                    />
                                </div>
                                <p class="text-xs text-surface-400">Recommended size: 64x64px. ICO or PNG.</p>
                             </div>
                         </div>
                     </div>
                 </div>

                 <hr class="border-surface-100 dark:border-surface-700" />

                 <!-- Appearance -->
                 <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                     <!-- Brand Color -->
                     <div class="space-y-3">
                        <label class="text-xs font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider">Brand Color</label>
                        <div class="flex items-center gap-3">
                             <div class="p-1 rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-0 shadow-sm">
                                <ColorPicker v-model="settings.brand_color" />
                             </div>
                             <div class="flex-1 bg-surface-50 border border-surface-200 dark:border-surface-700 rounded-lg px-3 py-2 flex items-center gap-2">
                                 <span class="text-surface-400 font-medium">#</span>
                                 <InputText v-model="settings.brand_color" class="flex-1 bg-transparent border-none p-0 focus:shadow-none text-surface-700 dark:text-surface-0 font-mono font-medium" :maxlength="6" />
                             </div>
                        </div>
                        <p class="text-xs text-surface-400">Primary color used for buttons, links, and accents.</p>
                     </div>

                     <!-- Theme Mode -->
                     <div class="space-y-3">
                        <label class="text-xs font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider">Theme Mode</label>
                        <SelectButton 
                            v-model="settings.theme_mode" 
                            :options="themeOptions" 
                            optionLabel="name" 
                            optionValue="value" 
                            class="w-full"
                            :pt="{ button: { class: 'flex-1' } }"
                        >
                            <template #option="slotProps">
                                <div class="flex items-center gap-2">
                                    <i :class="slotProps.option.icon"></i>
                                    <span>{{ slotProps.option.name }}</span>
                                </div>
                            </template>
                        </SelectButton>
                     </div>
                 </div>
             </div>
        </div>

        <!-- Email Settings -->
        <div class="rounded-xl shadow-sm border border-surface-200 dark:border-surface-700 overflow-hidden">
             <div class="p-6 border-b border-surface-100 dark:border-surface-700">
                <h2 class="text-lg font-bold text-surface-900 dark:text-surface-0">Email Settings</h2>
                <p class="text-sm text-surface-500 dark:text-surface-400 mt-1">Configure communication templates for your partners.</p>
             </div>
             
             <div class="p-6 space-y-6">
                 <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                     <!-- Invitation Template -->
                     <div class="space-y-3">
                        <label class="text-xs font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider">Invitation Email Template</label>
                        <Dropdown 
                            v-model="orgSettings.invitation_email_template" 
                            :options="emailTemplates.data" 
                            optionLabel="name" 
                            optionValue="name" 
                            placeholder="Select a template"
                            class="w-full rounded-xl"
                            showClear
                        />
                        <p class="text-xs text-surface-400">Template used when sending invitations to new partners.</p>
                     </div>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource, createListResource } from 'frappe-ui'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import InputText from 'primevue/inputtext'
import ColorPicker from 'primevue/colorpicker'
import SelectButton from 'primevue/selectbutton'
import Dropdown from 'primevue/dropdown'
import { useToast } from 'primevue/usetoast'
import { applyBrandColor } from '@/utils/branding'

// State
const loading = ref(true)
const saving = ref(false)
const settings = ref({
    logo: null,
    favicon: null,
    brand_color: '3b82f6',
    theme_mode: 'System'
})
const orgSettings = ref({
    invitation_email_template: null
})

const toast = useToast()

const themeOptions = [
    { name: 'System', value: 'System', icon: 'pi pi-desktop' },
    { name: 'Light', value: 'Light', icon: 'pi pi-sun' },
    { name: 'Dark', value: 'Dark', icon: 'pi pi-moon' }
]

// Current User's Org ID (We'll fetch doc based on this logic implicitly in backend, but here we just need to call get_list / get_doc logic wrapper)
// Wait, our doc.py logic gets the current org automatically.
// But we need the Organization Name (ID) to call get_doc. 
// Let's use get_list to find the org, or a specific endpoint. 
// Actually, doc.py has `get_current_org()` but it's internal.
// Let's use `frappe.auth.get_logged_user()` info to find org? 
// No, simpler: `referralpro.api.agency.doc.get_list` for Organization will return 1 record (the user's org).

const fetchSettings = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Organization',
        fields: JSON.stringify(['name', 'logo', 'favicon', 'brand_color', 'theme_mode']),
        page_length: 1
    },
    onSuccess: (data) => {
        if (data && data.length > 0) {
            const org = data[0]
            settings.value = {
                name: org.name,
                logo: org.logo,
                favicon: org.favicon,
                brand_color: org.brand_color ? org.brand_color.replace('#', '') : '3b82f6',
                theme_mode: org.theme_mode || 'System'
            }
            fetchOrgSettings.fetch()
        } else {
            loading.value = false
        }
    }
})

const fetchOrgSettings = createResource({
    url: 'referralpro.api.agency.doc.get_list',
    params: {
        doctype: 'Organization Setting',
        fields: JSON.stringify(['name', 'invitation_email_template']),
        page_length: 1
    },
    onSuccess: (data) => {
        if (data && data.length > 0) {
            orgSettings.value = {
                name: data[0].name,
                invitation_email_template: data[0].invitation_email_template
            }
        }
        loading.value = false
    }
})

const emailTemplates = createListResource({
    doctype: 'Email Template',
    fields: ['name'],
    auto: true
})

const saveResource = createResource({
    url: 'referralpro.api.agency.doc.save_doc',
    onSuccess: () => {
        saving.value = false
        toast.add({ severity: 'success', summary: 'Success', detail: 'Settings saved successfully', life: 3000 })
        applyTheme(settings.value.theme_mode)
        applyBrandColor(settings.value.brand_color)
    }
})

const saveSettings = () => {
    if (!settings.value.name) return
    saving.value = true
    
    // Save Organization Branding
    saveResource.submit({
        doctype: 'Organization',
        doc: {
            name: settings.value.name,
            logo: settings.value.logo,
            favicon: settings.value.favicon,
            brand_color: '#' + settings.value.brand_color,
            theme_mode: settings.value.theme_mode
        }
    })

    // Save Organization Settings
    saveResource.submit({
        doctype: 'Organization Setting',
        doc: {
            name: orgSettings.value.name || null, // Will create or update
            invitation_email_template: orgSettings.value.invitation_email_template
        }
    })
}

const customUploader = async (event, field) => {
    const file = event.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_private', 0);
    formData.append('folder', 'Home');

    try {
        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.csrf_token || '',
            },
            body: formData,
        });

        const data = await response.json();
        if (data.message) {
            settings.value[field] = data.message.file_url;
        }
    } catch (error) {
        console.error('Upload failed:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'File upload failed', life: 3000 })
    }
};


const applyTheme = (mode) => {
    if (mode == 'Dark') {   
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }

    // const html = document.documentElement
    // if (mode === 'Dark') {
    //     html.classList.add('dark')
    // } else if (mode === 'Light') {
    //     html.classList.remove('dark')
    // } else {
    //     // System
    //     if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    //         html.classList.add('dark')
    //     } else {
    //         html.classList.remove('dark')
    //     }
    // }
}

onMounted(() => {
    fetchSettings.fetch()
})

</script>

<style scoped>
:deep(.p-colorpicker-preview) {
    width: 2rem;
    height: 2rem;
    border-radius: 0.5rem;
}
</style>
