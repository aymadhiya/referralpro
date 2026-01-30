<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { Building2, Users, Save, Plus, Mail, Phone, MapPin, Pencil, Trash2 } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Card from 'primevue/card'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

// Profile State
const profile = ref({
    name: '',
    organization_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    tax_id: ''
})

// Directors State
const directors = ref([])
const showDirectorDialog = ref(false)
const directorForm = ref({
    email: '',
    firstname: '',
    lastname: '',
    phone: '',
    is_primary: 0
})
const editingDirectorIndex = ref(-1)

// Resources
const fetchProfile = createResource({
    url: 'referralpro.api.partner.partner.get_my_profile',
    onSuccess: (data) => {
        if (data) profile.value = data
    }
})

const updateProfile = createResource({
    url: 'referralpro.api.partner.partner.update_my_profile',
    onSuccess: (data) => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Profile updated successfully', life: 3000 })
        if (data.profile) profile.value = data.profile
    },
    onError: (err) => {
        toast.add({ severity: 'error', summary: 'Error', detail: err.message || 'Failed to update profile', life: 3000 })
    }
})

const fetchDirectors = createResource({
    url: 'referralpro.api.partner.partner.get_organization_contacts',
    onSuccess: (data) => {
        directors.value = data || []
    }
})

const saveDirectors = createResource({
    url: 'referralpro.api.partner.partner.save_organization_contacts',
    onSuccess: (data) => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Director details saved', life: 3000 })
        showDirectorDialog.value = false
        fetchDirectors.fetch()
    },
    onError: (err) => {
        toast.add({ severity: 'error', summary: 'Error', detail: err.message || 'Failed to save director', life: 3000 })
    }
})

onMounted(() => {
    fetchProfile.fetch()
    fetchDirectors.fetch()
})

// Handlers
const handleSaveProfile = () => {
    updateProfile.submit({
        data: profile.value
    })
}

const openDirectorDialog = (director = null) => {
    if (director) {
        directorForm.value = { ...director }
        // Find index if needed, but we rely on email/name matching in backend usually? 
        // Backend key is email.
        editingDirectorIndex.value = 1 
    } else {
        directorForm.value = {
            email: '',
            firstname: '',
            lastname: '',
            phone: '',
            is_primary: 0
        }
        editingDirectorIndex.value = -1
    }
    showDirectorDialog.value = true
}

const handleSaveDirector = () => {
    // Validate
    if (!directorForm.value.email || !directorForm.value.firstname) {
        toast.add({ severity: 'warn', summary: 'Validation', detail: 'Name and Email are required', life: 3000 })
        return
    }
    
    // Construct payload as a list of one director to update/create
    const payload = [{
        name: `${directorForm.value.firstname} ${directorForm.value.lastname || ''}`.trim(),
        firstname: directorForm.value.firstname,
        lastname: directorForm.value.lastname,
        email: directorForm.value.email,
        phone: directorForm.value.phone,
        is_primary: directorForm.value.is_primary
    }]
    
    saveDirectors.submit({
        contacts: JSON.stringify(payload)
    })
}

const getInitials = (fname, lname) => {
    return ((fname?.[0] || '') + (lname?.[0] || '')).toUpperCase()
}
</script>

<template>
  <div class="p-6 lg:p-12 max-w-[1400px] mx-auto font-sans min-h-screen">
    <Toast />
    
    <!-- Header -->
    <div class="mb-8">
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Organization Profile</h1>
        <p class="text-slate-500 font-medium">Manage your company details and authorized directors.</p>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden min-h-[600px]">
        <TabView :pt="{
            nav: { class: 'bg-slate-50 border-b border-slate-200 px-6' },
            inkbar: { class: 'bg-blue-600 h-1' },
            root: { class: 'flex-1 flex flex-col' },
            panelContainer: { class: 'p-8 lg:p-10' }
        }">
            
            <!-- ORGANIZATION DETAILS -->
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2 py-3">
                        <Building2 :size="18" />
                        <span class="font-bold">General Details</span>
                    </div>
                </template>
                
                <div v-if="fetchProfile.loading" class="flex justify-center py-20">
                     <div class="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
                </div>
                
                <div v-else class="max-w-4xl space-y-8">
                    <!-- Section: Identity -->
                    <div class="space-y-6">
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 border-b border-slate-100 pb-2">Business Identity</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Organization Name</label>
                                <InputText v-model="profile.organization_name" class="w-full" />
                            </div>
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Tax ID / EIN</label>
                                <InputText v-model="profile.tax_id" class="w-full" />
                            </div>
                        </div>
                    </div>

                    <!-- Section: Contact -->
                    <div class="space-y-6">
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 border-b border-slate-100 pb-2">Contact Info</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Main Email</label>
                                <InputText v-model="profile.email" disabled class="w-full bg-slate-50 text-slate-500" />
                                <small class="text-slate-400">Email cannot be changed directly.</small>
                            </div>
                            <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Phone</label>
                                <InputText v-model="profile.phone" class="w-full" />
                            </div>
                        </div>
                    </div>

                    <!-- Section: Address -->
                    <div class="space-y-6">
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 border-b border-slate-100 pb-2">Address</h3>
                        <div class="grid grid-cols-1 gap-6">
                             <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Street Address</label>
                                <InputText v-model="profile.address" class="w-full" />
                            </div>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                             <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">City</label>
                                <InputText v-model="profile.city" class="w-full" />
                            </div>
                             <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">State</label>
                                <InputText v-model="profile.state" class="w-full" />
                            </div>
                             <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Postal Code</label>
                                <InputText v-model="profile.postal_code" class="w-full" />
                            </div>
                             <div class="flex flex-col gap-2">
                                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Country</label>
                                <InputText v-model="profile.country" class="w-full" />
                            </div>
                        </div>
                    </div>

                    <div class="pt-6 border-t border-slate-100 flex justify-end">
                        <Button 
                            label="Save Changes" 
                            icon="pi pi-check" 
                            @click="handleSaveProfile" 
                            :loading="updateProfile.loading"
                        />
                    </div>
                </div>
            </TabPanel>

            <!-- DIRECTORS MANAGEMENT -->
            <TabPanel>
                <template #header>
                    <div class="flex items-center gap-2 py-3">
                        <Users :size="18" />
                        <span class="font-bold">Directors & Contacts</span>
                    </div>
                </template>

                 <div class="max-w-5xl space-y-8">
                    <div class="flex justify-between items-center">
                        <div class="space-y-1">
                            <h3 class="text-lg font-bold text-slate-900">Authorized Directors</h3>
                            <p class="text-slate-500 text-sm">Managing signatories for agreements.</p>
                        </div>
                        <Button label="Add Director" icon="pi pi-plus" size="small" @click="openDirectorDialog(null)" />
                    </div>
                    
                    <DataTable :value="directors" :loading="fetchDirectors.loading" class="p-datatable-sm border border-slate-200 rounded-lg overflow-hidden">
                        <template #empty>
                             <div class="text-center p-10 text-slate-500 italic">No directors found.</div>
                        </template>
                        
                        <Column header="Name">
                             <template #body="slotProps">
                                <div class="flex items-center gap-3">
                                    <div class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center text-xs font-bold">
                                        {{ getInitials(slotProps.data.firstname, slotProps.data.lastname) }}
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="font-bold text-slate-800 text-sm">{{ slotProps.data.firstname }} {{ slotProps.data.lastname }}</span>
                                        <span class="text-xs text-slate-400" v-if="slotProps.data.is_primary">Primary Contact</span>
                                    </div>
                                </div>
                            </template>
                        </Column>
                        
                        <Column field="email" header="Email"></Column>
                        <Column field="phone" header="Phone"></Column>
                        
                        <Column header="Status">
                            <template #body="slotProps">
                                <span class="inline-flex items-center px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
                                    :class="slotProps.data.signed ? 'bg-emerald-50 text-emerald-600' : 'bg-orange-50 text-orange-600'">
                                    {{ slotProps.data.signed ? 'Signed' : 'Pending' }}
                                </span>
                            </template>
                        </Column>

                        <Column header="Action" alignFrozen="right" frozen style="width: 100px">
                             <template #body="slotProps">
                                <div class="flex gap-2">
                                     <Button icon="pi pi-pencil" text rounded severity="secondary" size="small" @click="openDirectorDialog(slotProps.data)" />
                                </div>
                             </template>
                        </Column>
                    </DataTable>
                 </div>
            </TabPanel>
        </TabView>
    </div>

    <!-- DIRECTOR DIALOG -->
    <Dialog v-model:visible="showDirectorDialog" modal header="Director Details" :style="{ width: '500px' }">
        <div class="space-y-6 pt-4">
             <div class="grid grid-cols-2 gap-4">
                <div class="flex flex-col gap-2">
                    <label class="text-xs font-bold uppercase tracking-wider text-surface-500">First Name</label>
                    <InputText v-model="directorForm.firstname" class="w-full" />
                </div>
                <div class="flex flex-col gap-2">
                    <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Last Name</label>
                    <InputText v-model="directorForm.lastname" class="w-full" />
                </div>
            </div>

            <div class="flex flex-col gap-2">
                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Email Address</label>
                <InputText v-model="directorForm.email" class="w-full" :disabled="editingDirectorIndex === 1" />
                <small v-if="editingDirectorIndex === 1" class="text-slate-400">Email cannot be changed for existing director.</small>
            </div>

            <div class="flex flex-col gap-2">
                <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Phone</label>
                <InputText v-model="directorForm.phone" class="w-full" />
            </div>

            <div class="flex items-center gap-2 bg-slate-50 p-3 rounded-lg">
                <input type="checkbox" id="primaryCheck" v-model="directorForm.is_primary" :true-value="1" :false-value="0" class="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                <label for="primaryCheck" class="text-sm font-semibold text-slate-700">Set as Primary Contact</label>
            </div>
        </div>

        <template #footer>
            <Button label="Cancel" text severity="secondary" @click="showDirectorDialog = false" />
            <Button label="Save Director" icon="pi pi-save" @click="handleSaveDirector" :loading="saveDirectors.loading" />
        </template>
    </Dialog>

  </div>
</template>
