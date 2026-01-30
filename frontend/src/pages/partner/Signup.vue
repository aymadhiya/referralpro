<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import { Stars, Loader2, CheckCircle2 } from 'lucide-vue-next'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import SelectButton from 'primevue/selectbutton'
import Message from 'primevue/message'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const token = route.query.token

const loading = ref(true)
const verifying = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref(false)
const invitation = ref(null)
const redirectTarget = ref('')

const form = ref({
    password: '',
    confirm_password: '',
    partner_name: '',
    organization_name: '',
    partner_type: 'Company'
})

const typeOptions = ref(['Company', 'Individual'])

const hasPassword = ref(false)
const inviting_organization = ref('')

const verifyToken = createResource({
    url: 'referralpro.api.partner.auth.verify_invitation_token',
    params: { token },
    onSuccess: (result) => {
        if (result.success_key) {
            let data = result?.invitation
            invitation.value = data
            form.value.partner_name = data.partner_name
            form.value.organization_name = data.organization_name
            
            hasPassword.value = !!data.has_password
            inviting_organization.value = data.organization_title || data.organization
        
        // Removed logic that was here before? No, just adding variables.
            verifying.value = false
            loading.value = false
        } else {
            error.value = result.message
            verifying.value = false
            loading.value = false
        }
    },
    onError: (err) => {
        error.value = err.message || 'Invalid or expired invitation link'
        verifying.value = false
        loading.value = false
    }
})

const signupResource = createResource({
    url: 'referralpro.api.partner.auth.complete_signup',
    onSuccess: (data) => {
        success.value = true
        redirectTarget.value = data.redirect_to || '/partner/dashboard'
        submitting.value = false
        
        if (data.redirect_to) {
            router.push(data.redirect_to)
        } else {
            router.push('/partner/dashboard')
        }
    },
    onError: (err) => {
        error.value = err.message || 'Signup failed. Please try again.'
        toast.add({ severity: 'error', summary: 'Error', detail: error.value, life: 5000 })
        submitting.value = false
    }
})

const handleSignup = () => {
    // Validation
    if (!form.value.partner_name || !form.value.organization_name) {
        toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Name and Organization are required', life: 3000 })
        return
    }

    if (!hasPassword.value) {
        if (!form.value.password || !form.value.confirm_password) {
            toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Password fields are required', life: 3000 })
            return
        }

        if (form.value.password !== form.value.confirm_password) {
            toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Passwords do not match', life: 3000 })
            return
        }

        if (form.value.password.length < 5) {
             toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Password must be at least 5 characters', life: 3000 })
             return
        }
    }
    
    error.value = ''
    submitting.value = true
    signupResource.submit({
        token,
        password: form.value.password,
        partner_name: form.value.partner_name,
        organization_name: form.value.organization_name,
        partner_type: form.value.partner_type
    })
}

onMounted(() => {
    if (!token) {
        error.value = "Invitation token is missing"
        loading.value = false
        verifying.value = false
    } else {
        verifyToken.fetch()
    }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-50 font-sans py-12 px-4">
    <Toast />
    <div class="bg-surface-0 p-8 rounded-xl shadow-lg w-full max-w-[480px] border border-surface-200 dark:border-surface-800">
      
      <!-- Top Logo Section -->
      <div class="flex flex-col items-center justify-center mb-10 text-center">
        <h1 class="text-3xl font-black text-surface-900 dark:text-surface-0 tracking-tight mb-2">Partner Portal</h1>
        <p class="text-surface-500 dark:text-surface-400 font-medium">Join our referral network</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center py-12">
        <Loader2 class="w-10 h-10 text-emerald-600 animate-spin mb-4" />
        <p class="text-surface-500 font-medium tracking-wide">Securing your connection...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="space-y-6">
        <div class="p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 rounded-2xl flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center flex-shrink-0 text-red-600">
                <i class="pi pi-exclamation-triangle"></i>
            </div>
            <p class="text-sm font-bold text-red-600 dark:text-red-400 leading-snug">{{ error }}</p>
        </div>
        <Button label="Go back to Login" @click="router.push('/partner/login')" severity="secondary" class="w-full" />
      </div>

      <!-- Success State -->
      <div v-else-if="success" class="text-center py-8 space-y-4">
        <div class="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/20 rounded-full flex items-center justify-center mx-auto text-emerald-600 mb-6 group">
            <CheckCircle2 class="w-12 h-12 group-hover:scale-110 transition-transform" />
        </div>
        <h2 class="text-2xl font-black text-surface-900 dark:text-surface-0">Welcome!</h2>
        <p class="text-surface-500 font-medium">
            {{ redirectTarget === '/partner/setup-directors' ? 'Redirecting to Director Setup...' : 'Your account is ready. Redirecting you to your dashboard...' }}
        </p>
      </div>

      <!-- Signup Form -->
      <form v-else @submit.prevent="handleSignup" class="space-y-6">
        <div class="space-y-4">
            <div v-if="inviting_organization">
                <label class="block text-xs font-black text-surface-400 uppercase tracking-[0.1em] mb-2 px-1">Invited By</label>
                <InputText 
                    :value="inviting_organization" 
                    disabled
                    class="w-full" 
                />
            </div>
            <div>
                <label class="block text-xs font-black text-surface-400 uppercase tracking-[0.1em] mb-2 px-1">Your Name</label>
                <InputText 
                    v-model="form.partner_name" 
                    class="w-full" 
                />
            </div>
            <div>
                <label class="block text-xs font-black text-surface-400 uppercase tracking-[0.1em] mb-2 px-1">Organization Name</label>
                <InputText 
                    v-model="form.organization_name" 
                    class="w-full" 
                />
            </div>
            <div>
                <label class="block text-xs font-black text-surface-400 uppercase tracking-[0.1em] mb-2 px-1">Type</label>
                <SelectButton v-model="form.partner_type" :options="typeOptions" aria-labelledby="basic" class="w-full" />
            </div>
            
            <div v-if="!hasPassword" class="grid grid-cols-1 gap-4">
                <div class="space-y-2">
                    <label class="block text-xs font-black text-surface-400 uppercase tracking-[0.1em] px-1">Set Password</label>
                    <Password 
                        v-model="form.password" 
                        toggleMask 
                        class="w-full"
                        inputClass="w-full" 
                        :feedback="true"
                    />
                </div>
                 <div class="space-y-2">
                    <label class="block text-xs font-black text-surface-400 uppercase tracking-[0.1em] px-1">Confirm Password</label>
                    <Password 
                        v-model="form.confirm_password" 
                        toggleMask 
                        class="w-full"
                        inputClass="w-full" 
                        :feedback="false"
                    />
                </div>
            </div>
            <div v-else class="p-4 bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/20 rounded-2xl flex items-center gap-3">
                 <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0 text-blue-600">
                    <i class="pi pi-info-circle"></i>
                </div>
                <p class="text-sm font-medium text-blue-600 dark:text-blue-400 leading-snug">
                    You already have an account. We'll link this new partner organization to your existing user.
                </p>
            </div>
        </div>

        <div class="pt-4">
            <Button 
                type="submit" 
                :loading="submitting"
                :label="hasPassword ? 'Join Organization' : 'Start Referring'"
                class="w-full" 
            />
        </div>

        <p class="text-center text-[11px] text-surface-400 font-medium px-4">
            By joining, you agree to our Terms of Service and Privacy Policy.
        </p>
      </form>

    </div>
  </div>
</template>

<style scoped>
:deep(.p-password-input) {
  width: 100%;
}
</style>
