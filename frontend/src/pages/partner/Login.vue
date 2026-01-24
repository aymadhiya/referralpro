<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Stars } from 'lucide-vue-next'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    console.log('Logging in as Referral Partner:', email.value)
    // router.push('/partner/dashboard')
  } catch (err) {
    error.value = 'Invalid credentials. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50/50 font-sans px-4">
    <div class="bg-white p-10 rounded-[2rem] shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] w-full max-w-[440px] border border-slate-50">
      
      <!-- Top Logo Section -->
      <div class="flex items-center justify-center gap-4 mb-10">
        <div class="w-12 h-12 bg-emerald-600 rounded-xl flex items-center justify-center shadow-[0_8px_16px_-4px_rgba(5,150,105,0.5)]">
          <Stars class="text-white w-7 h-7" />
        </div>
        <h1 class="text-[28px] font-bold text-[#0f172a] tracking-tight">Partner Portal</h1>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Email Field -->
        <div class="space-y-2">
          <label for="email" class="block text-sm font-semibold text-slate-600 ml-1">Partner Email</label>
          <InputText 
            id="email"
            v-model="email" 
            class="w-full rounded-2xl border-slate-200 py-3.5 px-5 text-slate-700 bg-white focus:border-emerald-400 transition-all placeholder:text-slate-300 font-medium"
            placeholder="example@mail.com"
          />
        </div>

        <!-- Password Field -->
        <div class="space-y-2">
          <div class="flex justify-between items-center px-1">
            <label for="password" class="block text-sm font-semibold text-slate-600">Password</label>
            <a href="#" class="text-[13px] font-bold text-emerald-600 hover:text-emerald-700 transition-colors">Forgot?</a>
          </div>
          <Password 
            id="password"
            v-model="password" 
            :feedback="false"
            toggleMask
            class="w-full"
            inputClass="w-full rounded-2xl border-slate-200 py-3.5 px-5 text-slate-700 bg-white focus:border-emerald-400 transition-all font-medium"
            placeholder="••••••••"
          />
        </div>

        <!-- Submit Button -->
        <div class="pt-4">
          <Button 
            type="submit" 
            :loading="loading"
            class="w-full bg-[#0f172a] hover:bg-slate-900 border-none text-white font-bold py-4 rounded-2xl shadow-lg shadow-slate-200 transition-all duration-300"
          >
            <span class="text-lg text-emerald-50">Sign In</span>
          </Button>
        </div>
      </form>

      <Message v-if="error" severity="error" variant="simple" class="mt-4 text-sm font-bold text-red-600 px-1 text-center">
            {{ error }}
      </Message>

      <!-- Agency Login Link -->
      <div class="mt-8 pt-6 border-t border-slate-50 text-center">
        <p class="text-sm font-medium text-slate-500">
          Are you an agency owner?  
          <router-link to="/agency/login" class="text-emerald-600 font-bold hover:underline transition-all ml-1">
            Agency Login
          </router-link>
        </p>
      </div>

    </div>
  </div>
</template>

<style scoped>
:deep(.p-password-input) {
  width: 100%;
}
:deep(.p-inputtext:focus) {
    box-shadow: none !important;
}
</style>
