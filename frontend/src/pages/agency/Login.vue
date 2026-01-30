<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useSessionStore } from '../../store/session'

const router = useRouter()
const sessionStore = useSessionStore()
const email = ref('')
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await sessionStore.login(email.value, password.value, '/agency/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-50 font-sans">
    <div class="bg-surface-0 p-10 rounded-[2rem] shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] w-full max-w-[440px] border border-surface-200 dark:border-surface-800">
      
      <!-- Top Logo Section -->
      <div class="flex items-center justify-center gap-4 mb-10">
        <div class="w-12 h-12 bg-[#3b82f6] rounded-xl flex items-center justify-center shadow-[0_8px_16px_-4px_rgba(59,130,246,0.5)]">
          <span class="text-white text-2xl font-black">A</span>
        </div>
        <h1 class="text-[28px] font-bold text-surface-900 dark:text-surface-0 tracking-tight">Agency Portal</h1>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Email Field -->
        <div class="space-y-2">
          <label for="email" class="block text-sm font-semibold text-surface-600 dark:text-surface-400 ml-1">Email</label>
          <InputText 
            id="email"
            v-model="email" 
            class="w-full rounded-2xl border-surface-200 dark:border-surface-700 py-3.5 px-5 text-surface-700 dark:text-surface-0 bg-surface-0 focus:border-blue-400 transition-all placeholder:text-surface-300 dark:placeholder:text-surface-500 font-medium"
          />
        </div>

        <!-- Password Field -->
        <div class="space-y-2">
          <label for="password" class="block text-sm font-semibold text-surface-600 dark:text-surface-400 ml-1">Password</label>
          <Password 
            id="password"
            v-model="password" 
            :feedback="false"
            toggleMask
            class="w-full"
            inputClass="w-full rounded-2xl border-surface-200 dark:border-surface-700 py-3.5 px-5 text-surface-700 dark:text-surface-0 bg-surface-0 focus:border-blue-400 transition-all font-medium"
          />
        </div>

        <div class="pt-4">
          <Button 
            type="submit" 
            :loading="loading"
            label="Sign In"
            class="w-full py-4 text-lg font-bold"
          />
        </div>
      </form>

      <Message v-if="sessionStore.error" severity="error" variant="simple" class="mt-4 text-sm font-bold text-red-600 px-1 text-center">
            {{ sessionStore.error }}
      </Message>

      <!-- Signup Link -->
      <div class="mt-8 pt-6 border-t border-surface-100 dark:border-surface-800 text-center">
        <p class="text-sm font-medium text-surface-500 dark:text-surface-400">
          Don't have an agency? 
          <router-link to="/agency/signup" class="text-surface-900 dark:text-surface-0 font-bold hover:underline transition-all ml-1">
            Create Account
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
