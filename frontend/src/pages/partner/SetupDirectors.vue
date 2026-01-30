<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { Users, Plus, X, Check, Trash2, ArrowRight } from 'lucide-vue-next'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useSessionStore } from '../../store/session'

const router = useRouter()
const toast = useToast()
const sessionStore = useSessionStore()

const submitting = ref(false)
// Initialize with one empty row for better UX, or loading state
const directors = ref([])

const getContacts = createResource({
    url: 'referralpro.api.partner.partner.get_organization_contacts',
    onSuccess: (data) => {
        if (data && data.length > 0) {
            directors.value = data
        } else {
             // Default empty row with auto-fill from userInfo
            const userInfo = sessionStore.userInfo;
            let firstname = '';
            let lastname = '';
            if (userInfo?.full_name) {
                const parts = userInfo.full_name.trim().split(/\s+/);
                firstname = parts[0];
                lastname = parts.slice(1).join(' ');
            }
            directors.value = [{ 
                firstname: firstname, 
                lastname: lastname, 
                email: userInfo?.email || '', 
                phone: '', 
                is_primary: true 
            }]
        }
    }
})

onMounted(() => {
    getContacts.fetch()
})

const saveContacts = createResource({
    url: 'referralpro.api.partner.partner.save_organization_contacts',
    onSuccess: async (data) => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Directors added successfully', life: 3000 })
        
        // Refresh session to get updated Onboarding Status
        await sessionStore.getUserInfo()
        
        setTimeout(() => {
            router.push('/partner/dashboard')
        }, 1500)
    },
    onError: (err) => {
        toast.add({ severity: 'error', summary: 'Error', detail: err.message || 'Failed to save contacts', life: 5000 })
        submitting.value = false
    }
})

const addRow = () => {
    directors.value.push({
        firstname: '',
        lastname: '',
        email: '',
        phone: '',
        is_primary: directors.value.length === 0 
    })
}

const removeDirector = (index) => {
    directors.value.splice(index, 1)
    if (directors.value.length === 0) {
        addRow()
    }
}

const setPrimary = (index) => {
    directors.value.forEach((d, i) => d.is_primary = i === index)
}

const submitDirectors = () => {
    // Validation: All fields required
    if (directors.value.length === 0) {
        toast.add({ severity: 'error', summary: 'Validation', detail: 'Please add at least one director', life: 3000 })
        return
    }

    const invalidRow = directors.value.find(d => !d.firstname || !d.lastname || !d.email || !d.phone)
    if (invalidRow) {
         toast.add({ severity: 'error', summary: 'Validation', detail: 'All fields (First Name, Last Name, Email, Phone) are required for all directors.', life: 3000 })
         return
    }
    
    const hasPrimary = directors.value.some(d => d.is_primary)
    if (!hasPrimary) {
        // If only one, make it primary automatically?
        if (directors.value.length === 1) {
             directors.value[0].is_primary = true
        } else {
            toast.add({ severity: 'error', summary: 'Validation', detail: 'One director must be marked as Primary', life: 3000 })
            return
        }
    }

    // Construct full name for API compatibility
    const contactsToSend = directors.value.map(d => ({
        ...d,
        name: `${d.firstname} ${d.lastname}`.trim()
    }))

    submitting.value = true
    saveContacts.submit({
        contacts: JSON.stringify(contactsToSend)
    })
}
</script>

<template>
  <div class="min-h-screen bg-surface-50 font-sans p-6">
    <Toast />
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="bg-surface-0 rounded-xl p-8 mb-6 shadow-sm border border-surface-200">
            <div class="flex items-start gap-6">
                <div class="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center flex-shrink-0 text-emerald-600">
                    <Users class="w-8 h-8" />
                </div>
                <div>
                    <h1 class="text-2xl font-bold text-surface-900 mb-2">Setup Directors</h1>
                    <p class="text-surface-500 max-w-2xl">
                        Since your organization requires a formal agreement, please add the details of your company directors. 
                        They will receive an email to sign the agreement.
                    </p>
                </div>
            </div>
        </div>

        <!-- Directors Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-24">
            
            <!-- Director Cards -->
            <div v-for="(director, index) in directors" :key="index" class="relative group bg-surface-0 rounded-xl p-6 shadow-sm border border-surface-200 hover:shadow-md transition-shadow">
                <!-- Card Header / Primary Badge -->
                <div class="flex justify-between items-start mb-4">
                     <div class="w-10 h-10 rounded-full bg-surface-100 flex items-center justify-center text-surface-500 font-bold text-lg border border-surface-200">
                        {{ index + 1 }}
                    </div>
                    <div class="flex gap-2">
                         <Button 
                            @click="setPrimary(index)"
                            :label="director.is_primary ? 'Primary' : 'Set as Primary'"
                            :icon="director.is_primary ? 'pi pi-check' : 'pi pi-user'"
                            text
                            rounded
                            size="small"
                            :severity="director.is_primary ? 'success' : 'secondary'"
                        />
                        <Button 
                            icon="pi pi-trash"
                            text
                            rounded
                            severity="danger"
                            @click="removeDirector(index)"
                        />
                    </div>
                </div>

                <!-- Fields -->
                <div class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="flex flex-col gap-2">
                            <label class="text-xs font-bold uppercase tracking-wider text-surface-500">First Name</label>
                            <InputText v-model="director.firstname" class="w-full" />
                        </div>
                        <div class="flex flex-col gap-2">
                             <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Last Name</label>
                             <InputText v-model="director.lastname" class="w-full" />
                        </div>
                    </div>
                    <div class="flex flex-col gap-2">
                         <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Email</label>
                         <InputText v-model="director.email" class="w-full" />
                    </div>
                    <div class="flex flex-col gap-2">
                         <label class="text-xs font-bold uppercase tracking-wider text-surface-500">Phone</label>
                         <InputText v-model="director.phone" class="w-full" />
                    </div>
                </div>
            </div>

            <!-- Add Button Card -->
            <Button 
                @click="addRow"
                text
                severity="secondary"
                class="flex flex-col items-center justify-center min-h-[300px] rounded-xl border-dashed border-2 border-surface-300 transition-all hover:bg-surface-50 group"
            >
                <div class="w-12 h-12 rounded-full border border-surface-300 flex items-center justify-center mb-3 group-hover:bg-primary-50 group-hover:border-primary-500">
                    <Plus class="w-6 h-6" />
                </div>
                <span class="font-bold">Add Another Director</span>
            </Button>
        </div>

        <!-- Submit Footer -->
        <div class="fixed bottom-0 left-0 right-0 p-6 bg-surface-0 border-t border-surface-200 flex justify-center z-10 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)]">
            <div class="w-full max-w-6xl flex justify-between items-center px-4">
                <div class="text-surface-500 font-medium hidden md:block text-sm">
                    Ensure the <strong>Primary Contact</strong> is correctly selected.
                </div>
                <Button 
                    @click="submitDirectors" 
                    :loading="submitting"
                    label="Save" 
                    icon="pi pi-check" 
                    iconPos="right"
                />
            </div>
        </div>

    </div>
  </div>
</template>
