<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createListResource, createResource } from 'frappe-ui'
import { Plus, Users, Search, MoreHorizontal, Mail, Phone, MapPin, Trash2, AlertTriangle } from 'lucide-vue-next'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const activeMenu = ref(null)
const confirmDeleteVisible = ref(false)
const partnerToDelete = ref(null)
const viewDetailsDialog = ref(false)
const selectedPartner = ref(null)

const contacts = createListResource({
    doctype: 'Organization Contacts',
    fields: ['name', 'firstname', 'lastname', 'email', 'phone', 'is_primary', 'status', 'signed', 'signed_date', 'signature_image'],
    filters: {},
    auto: false
})

const partners = createListResource({
    doctype: 'Organization',
    fields: ['name', 'organization_name', 'partner_name', 'email', 'status', 'onboarding_status', 'creation', 'logo', 'type'],
    filters: {
        organization_type: 'Referral Partner'
    },
    orderBy: 'creation desc',
    pageLength: 20
})

const inviteDialogVisible = ref(false)
const inviteForm = ref({
    partner_name: '',
    organization_name: '',
    email: ''
})

const createPartner = createResource({
    url: 'referralpro.api.agency.doc.save_doc',
    onSuccess: () => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Partner invited successfully', life: 3000 })
        inviteDialogVisible.value = false
        inviteForm.value = { partner_name: '', organization_name: '', email: '' }
        partners.reload()
    }
})

const deleteResource = createResource({
    url: 'referralpro.api.agency.doc.delete_doc',
    onSuccess: () => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Partner deleted successfully', life: 3000 })
        confirmDeleteVisible.value = false
        partnerToDelete.value = null
        partners.reload()
    }
})

const confirmDelete = (partner) => {
    partnerToDelete.value = partner
    confirmDeleteVisible.value = true
    activeMenu.value = null
}

const showDetails = (partner) => {
    selectedPartner.value = partner
    viewDetailsDialog.value = true
    contacts.filters = { referral_partner: partner.name }
    contacts.reload()
}

const deletePartner = () => {
    if (!partnerToDelete.value) return
    
    deleteResource.submit({
        doctype: 'Organization',
        name: partnerToDelete.value.name
    })
}

const submitInvite = () => {
    if (!inviteForm.value.partner_name || !inviteForm.value.organization_name || !inviteForm.value.email) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'All fields are required', life: 3000 })
        return
    }

    createPartner.submit({
        doctype: 'Referral Partner Invitation',
        doc: {
            partner_name: inviteForm.value.partner_name,
            organization_name: inviteForm.value.organization_name,
            email: inviteForm.value.email
        }
    })
}

const getStatusColor = (status) => {
    switch(status) {
        case 'Pending Director Setup': return 'bg-orange-100 text-orange-700'
        case 'Pending Agreement': return 'bg-blue-100 text-blue-700'
        case 'Completed': return 'bg-emerald-100 text-emerald-700'
        default: return 'bg-surface-100 text-surface-600'
    }
}

onMounted(() => {
    partners.reload()
    if (route.query.invite === 'true') {
        inviteDialogVisible.value = true
    }
})
</script>

<template>
  <div class="p-8 max-w-[1600px] mx-auto">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-0 tracking-tight">Partners</h1>
        <p class="text-surface-500 dark:text-surface-400 mt-1">Manage all your referral partners.</p>
      </div>
      <Button 
        @click="inviteDialogVisible = true"
        label="Invite Partner"
        icon="pi pi-plus"
        class="shadow-lg"
      />
    </div>

    <!-- Search & Filters -->
    <div class="mb-6 flex gap-4">
        <div class="relative max-w-md w-full">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" :size="20" />
            <input 
                type="text" 
                placeholder="Search partners..." 
                class="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all text-surface-900 dark:text-surface-0"
            >
        </div>
    </div>

    <!-- Grid -->
    <div v-if="partners.data && partners.data.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div 
        v-for="partner in partners.data" 
        :key="partner.name"
        @click="showDetails(partner)"
        class="bg-white dark:bg-surface-900 p-5 rounded-2xl border border-surface-100 dark:border-surface-800 shadow-sm hover:shadow-md transition-all group cursor-pointer"
      >
        <div class="flex justify-between items-start mb-4">
            <div class="flex items-center gap-3">
                <div v-if="partner.logo" class="w-12 h-12 rounded-xl border border-surface-100 dark:border-surface-700 overflow-hidden bg-surface-50 dark:bg-surface-800 flex items-center justify-center">
                    <img :src="partner.logo" class="w-full h-full object-contain" />
                </div>
                <div class="w-12 h-12 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center text-lg font-bold">
                    {{ (partner.organization_name || partner.partner_name).charAt(0) }}
                </div>
                <div>
                    <h6 class="font-bold text-surface-900 dark:text-surface-0 leading-tight truncate max-w-[200px]" :title="partner.organization_name">{{ partner.organization_name }}</h6>
                    <p class="text-[10px] text-surface-500 font-medium uppercase mt-1">{{ partner.partner_name }} | {{  partner.type }}</p>
                </div>
            </div>
            <div class="relative">
                <Button 
                    @click.stop="activeMenu = activeMenu === partner.name ? null : partner.name" 
                    icon="pi pi-ellipsis-h"
                    text
                    rounded
                    class="!p-2 text-surface-400"
                />
                
                <!-- Dropdown Menu -->
                <div v-if="activeMenu === partner.name" class="absolute right-0 mt-2 w-48 bg-white dark:bg-surface-800 rounded-xl shadow-xl border border-surface-100 dark:border-surface-700 z-10 py-1 overflow-hidden">
                    <Button 
                        @click="showDetails(partner)" 
                        label="View Details"
                        icon="pi pi-users"
                        text
                        class="w-full !justify-start !px-4 !py-3 font-medium !text-surface-700 dark:!text-surface-200"
                    />
                    <Button 
                        @click="confirmDelete(partner)" 
                        label="Delete Partner"
                        icon="pi pi-trash"
                        severity="danger"
                        text
                        class="w-full !justify-start !px-4 !py-3 font-medium"
                    />
                </div>
                
                <!-- Backdrop for closing menu -->
                <div v-if="activeMenu === partner.name" @click="activeMenu = null" class="fixed inset-0 z-0 cursor-default"></div>
            </div>
        </div>

        <div class="space-y-3 mb-5">
            <div class="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400">
                <Mail :size="14" />
                <span class="truncate">{{ partner.email }}</span>
            </div>

        </div>
        
        <div class="flex items-center justify-between pt-4 border-t border-surface-100 dark:border-surface-800">
             <span 
                class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider"
                :class="getStatusColor(partner.onboarding_status)"
            >
                {{ partner.onboarding_status || 'Pending' }}
            </span>
            <span class="text-xs text-surface-400">Invited {{ partner.creation ? partner.creation.split(' ')[0] : '' }}</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!partners.loading" class="flex flex-col items-center justify-center min-h-[400px] bg-surface-50/50 dark:bg-surface-800/10 rounded-3xl border-2 border-dashed border-surface-200 dark:border-surface-700">
        <div class="p-4 bg-white dark:bg-surface-900 rounded-full shadow-sm mb-4">
            <Users :size="32" class="text-surface-400" />
        </div>
        <h3 class="text-lg font-bold text-surface-900 dark:text-surface-0 mb-1">No partners found</h3>
        <p class="text-surface-500 dark:text-surface-400 text-sm mb-6 max-w-xs text-center">Start growing your network by inviting your first referral partner.</p>
        <Button 
            @click="inviteDialogVisible = true"
            label="Invite First Partner"
            text
            class="font-bold underline"
        />
    </div>

    <!-- Invite Dialog -->
    <Dialog v-model:visible="inviteDialogVisible" modal header="Invite Partner" :style="{ width: '500px' }">
        <div class="space-y-4">
            <div class="flex flex-col gap-2">
                <label class="text-sm font-semibold text-surface-700 dark:text-surface-200">Organization Name *</label>
                <InputText v-model="inviteForm.organization_name" placeholder="e.g. Acme Corp" />
            </div>
            <div class="flex flex-col gap-2">
                <label class="text-sm font-semibold text-surface-700 dark:text-surface-200">Partner (Contact) Name *</label>
                <InputText v-model="inviteForm.partner_name" placeholder="Full Name" />
            </div>
             <div class="flex flex-col gap-2">
                <label class="text-sm font-semibold text-surface-700 dark:text-surface-200">Email Address *</label>
                <InputText v-model="inviteForm.email" placeholder="partner@example.com" />
            </div>
        </div>
        <template #footer>
            <div class="flex items-center justify-end gap-2 pt-4">
                <Button label="Cancel" text @click="inviteDialogVisible = false" class="font-semibold" />
                <Button label="Send Invitation" @click="submitInvite" :loading="createPartner.loading" class="px-6 font-bold" />
            </div>
        </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="confirmDeleteVisible" modal header="Delete Partner" :style="{ width: '400px' }">
        <div class="flex flex-col items-center text-center p-4">
            <div class="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center text-red-600 mb-4">
                <AlertTriangle :size="32" />
            </div>
            <h3 class="text-lg font-bold text-surface-900 dark:text-surface-0 mb-2">Are you sure?</h3>
            <p class="text-surface-500 dark:text-surface-400 text-sm mb-6">
                This will permanently delete the invitation for 
                <span class="font-bold text-surface-900 dark:text-surface-0">{{ partnerToDelete?.organization_name }}</span>.
                This action cannot be undone.
            </p>
            
            <div class="flex items-center gap-3 w-full">
                <Button label="Cancel" text @click="confirmDeleteVisible = false" class="flex-1 font-semibold" />
                <Button label="Delete" @click="deletePartner" severity="danger" :loading="deleteResource.loading" class="flex-1 font-bold" />
            </div>
        </div>
    </Dialog>

    <!-- Partner Details Dialog -->
    <Dialog v-model:visible="viewDetailsDialog" modal :header="selectedPartner?.organization_name || 'Partner Details'" :style="{ width: '800px' }" class="p-details-dialog">
        <div v-if="selectedPartner" class="space-y-8">
            <!-- Basic Info -->
            <div class="grid grid-cols-2 gap-8 bg-surface-50 dark:bg-surface-900/50 p-6 rounded-2xl border border-surface-100 dark:border-surface-800">
                <div class="space-y-4">
                    <div>
                        <label class="text-[10px] uppercase font-bold text-surface-400 block mb-1">Organization</label>
                        <p class="font-bold text-surface-900 dark:text-surface-0">{{ selectedPartner.organization_name }}</p>
                    </div>
                    <div>
                        <label class="text-[10px] uppercase font-bold text-surface-400 block mb-1">Partner Name</label>
                        <p class="font-bold text-surface-900 dark:text-surface-0">{{ selectedPartner.partner_name }}</p>
                    </div>
                </div>
                <div class="space-y-4">
                    <div>
                        <label class="text-[10px] uppercase font-bold text-surface-400 block mb-1">Email</label>
                        <p class="font-bold text-surface-900 dark:text-surface-0">{{ selectedPartner.email }}</p>
                    </div>
                    <div>
                        <label class="text-[10px] uppercase font-bold text-surface-400 block mb-1">Onboarding Status</label>
                        <span 
                            class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider"
                            :class="getStatusColor(selectedPartner.onboarding_status)"
                        >
                            {{ selectedPartner.onboarding_status || 'Pending' }}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Contacts Section -->
            <div>
                <div class="flex items-center justify-between mb-4 px-2">
                    <h3 class="text-lg font-bold text-surface-900 dark:text-surface-0 flex items-center gap-2">
                        <Users :size="20" class="text-primary-600" />
                        Partner Contacts
                    </h3>
                    <span v-if="contacts.data" class="text-xs font-medium text-surface-500">{{ contacts.data.length }} Contact(s) found</span>
                </div>

                <div v-if="contacts.loading" class="flex justify-center py-10">
                    <i class="pi pi-spin pi-spinner text-2xl text-primary-600"></i>
                </div>
                <div v-else-if="contacts.data && contacts.data.length > 0" class="space-y-4">
                    <div v-for="contact in contacts.data" :key="contact.name" class="p-5 border border-surface-200 dark:border-surface-800 rounded-2xl bg-white dark:bg-surface-900 shadow-sm hover:shadow-md transition-all">
                        <div class="flex justify-between items-start mb-4">
                            <div>
                                <h4 class="font-bold text-surface-900 dark:text-surface-0 flex items-center gap-2">
                                    {{ contact.firstname }} {{ contact.lastname }}
                                    <span v-if="contact.is_primary" class="bg-primary-50 text-primary-600 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">Primary</span>
                                </h4>
                                <div class="flex items-center gap-4 mt-1">
                                    <div class="flex items-center gap-1.5 text-xs text-surface-500 font-medium">
                                        <Mail :size="12" />
                                        {{ contact.email }}
                                    </div>
                                    <div class="flex items-center gap-1.5 text-xs text-surface-500 font-medium">
                                        <Phone :size="12" />
                                        {{ contact.phone || 'N/A' }}
                                    </div>
                                </div>
                            </div>
                            <div class="text-right">
                                <span 
                                    class="px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest border"
                                    :class="contact.signed ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-orange-50 text-orange-600 border-orange-100'"
                                >
                                    {{ contact.signed ? 'Signed' : 'Not Signed' }}
                                </span>
                            </div>
                        </div>

                        <!-- Signing Details -->
                        <div v-if="contact.signed" class="mt-4 pt-4 border-t border-surface-100 dark:border-surface-800 grid grid-cols-2 gap-4">
                            <div>
                                <label class="text-[10px] uppercase font-bold text-surface-400 block mb-1">Signed Date</label>
                                <p class="text-xs font-bold text-surface-700 dark:text-surface-300">{{ contact.signed_date ? contact.signed_date.split('.')[0] : 'N/A' }}</p>
                            </div>
                            <div v-if="contact.signature_image" class="text-right">
                                <label class="text-[10px] uppercase font-bold text-surface-400 block mb-1">Signature</label>
                                <div class="flex justify-end">
                                    <img :src="contact.signature_image" class="h-10 object-contain bg-white rounded border border-surface-200 p-1" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="text-center py-12 bg-surface-50 dark:bg-surface-900/50 rounded-2xl border-2 border-dashed border-surface-200 dark:border-surface-800">
                    <Users :size="32" class="text-surface-300 mx-auto mb-3" />
                    <p class="text-surface-500 font-medium">No contacts found for this partner</p>
                </div>
            </div>
        </div>
        <template #footer>
            <div class="pt-4 border-t border-surface-100 dark:border-surface-800">
                <Button label="Close" text @click="viewDetailsDialog = false" class="font-bold text-surface-600" />
            </div>
        </template>
    </Dialog>
  </div>
</template>

<style scoped>
/* Detail Dialog Styling */
:deep(.p-details-dialog .p-dialog-header) {
    padding: 1.5rem 1.5rem 1rem;
    border-bottom: 1px solid #f1f5f9;
}
:deep(.p-details-dialog .p-dialog-content) {
    padding: 1.5rem;
}
:deep(.dark .p-details-dialog .p-dialog-header) {
    border-bottom-color: #1e293b;
}
</style>
