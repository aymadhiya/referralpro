<script setup>
import { useRouter } from 'vue-router'
import { Clock, Mail, CheckCircle2 } from 'lucide-vue-next'
import Button from 'primevue/button'

const router = useRouter()
// Verification screen logic


</script>

<template>
  <div class="min-h-screen bg-surface-50 flex items-center justify-center p-4 font-sans">
    <div class="bg-surface-0 rounded-xl p-8 shadow-lg border border-surface-200 max-w-lg w-full text-center">
        
        <div class="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mx-auto mb-6 text-amber-600">
            <Clock class="w-6 h-6" />
        </div>

        <h1 class="text-2xl font-bold text-surface-900 mb-3">Verification Pending</h1>
        
        <p class="text-surface-600 mb-8 leading-relaxed">
            Thank you for setting up your directors. We have sent agreement emails to all listed contacts. 
            <br/><br/>
            Please ensure all agreements are signed. Once completed, your account will be activated automatically.
        </p>

        <div class="bg-surface-50 rounded-lg p-4 mb-8 text-left space-y-3">
            <div class="flex items-start gap-3">
                <Mail class="w-5 h-5 text-surface-400 mt-0.5" />
                <div>
                    <span class="block font-bold text-surface-700 text-sm">Check your inbox</span>
                    <span class="text-xs text-surface-500">Agreements have been sent to provided emails.</span>
                </div>
            </div>
             <div class="flex items-start gap-3">
                <CheckCircle2 class="w-5 h-5 text-surface-400 mt-0.5" />
                <div>
                    <span class="block font-bold text-surface-700 text-sm">Sign Documents</span>
                    <span class="text-xs text-surface-500">Directors must sign to proceed.</span>
                </div>
            </div>
        </div>

        <Button 
            label="Refresh Status" 
            @click="router.go(0)"
            class="w-full"
        />
        
        <div class="mt-4">
             <Button 
                label="Logout" 
                text
                severity="secondary"
                @click="router.push('/partner/login')"
                class="w-full"
            />
        </div>

    </div>
  </div>
</template>
