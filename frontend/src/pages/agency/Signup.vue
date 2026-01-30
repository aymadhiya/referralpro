<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const router = useRouter()
const form = ref({
  agencyName: '',
  agencyType: 'Company',
  adminName: '',
  email: '',
  phone: ''
})

const agencyTypes = ref([
    { name: 'Company', value: 'Company' },
    { name: 'Individual', value: 'Individual' }
]);

const loading = ref(false)
const errorMessage = ref('')
const submitted = ref(false)

const handleSignup = async () => {
    submitted.value = true
    
    // Basic Client Side Validation
    if(!form.value.agencyName || !form.value.adminName || !form.value.email || !form.value.phone) {
        errorMessage.value = "All fields are required"
        return
    }

  loading.value = true
  errorMessage.value = ''

  const data = await createResource({
    url: 'referralpro.api.agency.auth.signup',
    method: 'POST',
    params: {
        organization: form.value.agencyName,
        org_type: form.value.agencyType,
        email: form.value.email,
        full_name: form.value.adminName,
        mobile_no: form.value.phone
    },
    auto:true,
    onSuccess(data) {
      loading.value = false
      if (data.redirect_to) {
        window.location.href = data.redirect_to
      } else {
        // router.push('/agency/login')
      }
    },
    onError(error) {
      loading.value = false
      if (error.messages) {
          errorMessage.value = error.messages.join('\n')
      } else {
          errorMessage.value = error.message || 'An error occurred during signup'
      }
    }
  })  
  // const res = await data.fetch();
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-50 font-sans py-12">
    <div class="bg-surface-0 p-10 rounded-[2rem] shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] w-full max-w-[440px] border border-surface-200 dark:border-surface-800">
      
      <!-- Top Logo Section -->
      <div class="flex flex-col items-center justify-center mb-8">
        <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-12 bg-[#3b82f6] rounded-xl flex items-center justify-center shadow-[0_8px_16px_-4px_rgba(59,130,246,0.5)]">
            <span class="text-white text-2xl font-black">R</span>
            </div>
            <h1 class="text-[28px] font-bold text-surface-900 dark:text-surface-0 tracking-tight">Referral Portal</h1>
        </div>
        <h2 class="text-lg font-bold text-surface-900 dark:text-surface-0 tracking-tight">Create Agency Workspace</h2>
      </div>

       <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 text-red-600 dark:text-red-400 rounded-lg text-sm font-medium text-center">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleSignup" class="space-y-5">
        
        <!-- Agency Name -->
        <div>
            <label for="agencyName" class="form-label">Agency Name</label>
            <InputText 
                id="agencyName"
                v-model="form.agencyName" 
                class="w-full"
                :invalid="submitted && !form.agencyName"
            />
        </div>

         <!-- Agency Type -->
        <div>
            <label for="agencyType" class="form-label">Agency Type</label>
             <Dropdown 
                id="agencyType"
                v-model="form.agencyType" 
                :options="agencyTypes" 
                optionLabel="name" 
                optionValue="value"
                placeholder="Select a Type" 
                class="w-full h-[42px] flex items-center"
            />
        </div>

        <!-- Admin Full Name -->
        <div>
            <label for="adminName" class="form-label">Full Name</label>
            <InputText 
                id="adminName"
                v-model="form.adminName" 
                class="w-full"
                :invalid="submitted && !form.adminName"
            />
        </div>

        <!-- Work Email -->
        <div>
            <label for="email" class="form-label">Email</label>
            <InputText 
                id="email"
                v-model="form.email" 
                class="w-full"
                :invalid="submitted && !form.email"
            />
        </div>

        <!-- Phone -->
        <div>
            <label for="phone" class="form-label">Phone</label>
            <InputText 
                id="phone"
                v-model="form.phone" 
                class="w-full"
                :invalid="submitted && !form.phone"
            />
        </div>



        <!-- Submit Button -->
        <div class="pt-2">
          <Button 
            type="submit" 
            :loading="loading"
            label="Create Account"
            icon="pi pi-arrow-right"
            iconPos="right"
            class="w-full"
          />
        </div>
      </form>

      <!-- Footer -->
      <div class="mt-8 pt-6 border-t border-surface-100 dark:border-surface-800 text-center">
        <p class="text-sm font-medium text-surface-500 dark:text-surface-400">
          Already have an account? 
          <router-link to="/agency/login" class="text-blue-600 font-bold hover:underline transition-all ml-1">
            Sign In
          </router-link>
        </p>
      </div>

    </div>
  </div>
</template>

<style scoped>

:deep(.p-inputtext:focus) {
    box-shadow: none !important;
}
:deep(.p-dropdown:focus) {
    box-shadow: none !important;
}
</style>
