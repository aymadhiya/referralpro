<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Stars } from 'lucide-vue-next'
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
    await sessionStore.login(email.value, password.value, '/partner/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-50 font-sans px-4">
    <div class="bg-surface-0 p-8 rounded-xl shadow-lg w-full max-w-[440px] border border-surface-200 dark:border-surface-800">
      
      <!-- Top Logo Section -->
      <div class="flex flex-col items-center justify-center gap-4 mb-10">
        <div class="w-12 h-12 bg-emerald-600 rounded-lg flex items-center justify-center">
          <Stars class="text-white w-7 h-7" />
        </div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 tracking-tight">Partner Portal</h1>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Email Field -->
        <div class="space-y-2">
          <label for="email" class="block text-sm font-semibold text-surface-600 dark:text-surface-400 ml-1">Partner Email</label>
          <InputText 
            id="email"
            v-model="email" 
            class="w-full"
          />
        </div>

        <!-- Password Field -->
        <div class="space-y-2">
          <div class="flex justify-between items-center px-1">
            <label for="password" class="block text-sm font-semibold text-surface-600 dark:text-surface-400">Password</label>
            <a href="#" class="text-[13px] font-bold text-emerald-600 hover:text-emerald-700 transition-colors">Forgot?</a>
          </div>
          <Password 
            id="password"
            v-model="password" 
            :feedback="false"
            toggleMask
            class="w-full"
            inputClass="w-full"
          />
        </div>

        <div class="pt-4">
          <Button 
            type="submit" 
            :loading="loading"
            label="Sign In"
            class="w-full"
          />
        </div>
      </form>

      <Message v-if="sessionStore.error" severity="error" variant="simple" class="mt-4 text-sm font-bold text-red-600 px-1 text-center">
            {{ sessionStore.error }}
      </Message>

      <!-- Agency Login Link -->
      <div class="mt-8 pt-6 border-t border-surface-100 dark:border-surface-800 text-center">
        <p class="text-sm font-medium text-surface-500 dark:text-surface-400">
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
</style>
