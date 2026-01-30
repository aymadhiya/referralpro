<script setup>
import { ref, onMounted, nextTick, createApp, h, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import { CheckCircle2, FileText, AlertCircle } from 'lucide-vue-next'
import SignatureSection from '../../components/SignatureSection.vue'

const route = useRoute()
const contactId = route.params.id

const loading = ref(true)
const error = ref(null)
const agreementData = ref(null)
const signedSuccess = ref(false)
const alreadySigned = ref(false)
const submitting = ref(false)
const teleportTarget = ref(null)

const fetchInfo = createResource({
    url: 'referralpro.api.public.get_signing_info',
    params: { contact_name: contactId },
    onSuccess: (data) => {
        agreementData.value = data
        if (data.already_signed) {
            alreadySigned.value = true
        }
        loading.value = false
        // Find placeholder after DOM update
        nextTick(() => {
            const el = document.querySelector('.signature_required')
            if (el) {
                el.id = 'signature-teleport-target'
                el.innerHTML = '' // Clear placeholder
                teleportTarget.value = '#signature-teleport-target'
            }
        })
    },
    onError: (err) => {
        error.value = err.message || 'Failed to load agreement details.'
        loading.value = false
    }
})

const signAction = createResource({
    url: 'referralpro.api.public.sign_agreement',
    onSuccess: (data) => {
        signedSuccess.value = true
        submitting.value = false
        window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    onError: (err) => {
        error.value = err.message || 'Failed to sign agreement.'
        submitting.value = false
    }
})

const handleSigned = (payload) => {
    submitting.value = true
    signAction.submit({ 
        contact_name: contactId,
        details: payload.details,
        signature_data: payload.signature_data
    })
}

onMounted(() => {
    if (contactId) {
        fetchInfo.fetch()
    } else {
        error.value = "Invalid Link"
        loading.value = false
    }
})
</script>

<template>
  <div class="min-h-screen bg-surface-50 flex items-center justify-center p-4 font-sans">
    <div class="w-full max-w-3xl bg-surface-0 rounded-[2rem] shadow-sm border border-surface-200 overflow-hidden">
        
        <!-- Loading State -->
        <div v-if="loading" class="p-12 flex flex-col items-center justify-center text-center">
            <div class="animate-spin w-8 h-8 border-4 border-surface-200 border-t-emerald-600 rounded-full mb-4"></div>
            <p class="text-surface-500 font-medium">Loading Agreement...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="p-12 flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center text-red-500 mb-4">
                <AlertCircle class="w-8 h-8" />
            </div>
             <h2 class="text-xl font-bold text-surface-900 mb-2">Unavailable</h2>
            <p class="text-surface-500">{{ error }}</p>
        </div>

        <!-- Success State (After Signing) -->
        <div v-else-if="signedSuccess" class="p-12 flex flex-col items-center justify-center text-center">
             <div class="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 mb-6">
                <CheckCircle2 class="w-10 h-10" />
            </div>
            <h1 class="text-2xl font-black text-surface-900 mb-3">Agreement Signed</h1>
            <p class="text-surface-600 max-w-md mx-auto">
                Thank you, <strong>{{ agreementData?.contact?.firstname }}</strong>. You have successfully signed the agreement for <strong>{{ agreementData?.agency_name }}</strong>.
            </p>
        </div>

        <!-- Agreement Content -->
        <div v-else class="flex flex-col h-[85vh] md:h-auto">
            <!-- Header -->
            <div class="p-8 border-b border-surface-200 bg-surface-50/50">
                 <div class="flex items-center gap-4 mb-2">
                    <div class="w-10 h-10 bg-surface-200 rounded-xl flex items-center justify-center text-surface-600">
                        <FileText class="w-5 h-5" />
                    </div>
                    <div>
                        <h2 class="font-bold text-surface-900 text-lg">{{ agreementData?.agency_name }} Partner Agreement</h2>
                        <p class="text-sm text-surface-500">Please review the terms below carefully.</p>
                    </div>
                </div>
            </div>
            
            <!-- Scrollable Content -->
            <div class="flex-1 overflow-y-auto p-8 bg-surface-0 prose prose-sm max-w-none text-surface-700">
                <div v-html="agreementData?.html_content || '<p>No content loaded.</p>'"></div>
            </div>

            <!-- Footer Action -->
            <div class="p-6 border-t border-surface-200 bg-surface-50">
                 <div class="text-sm text-surface-500 text-center">
                    Signing as <strong>{{ agreementData?.contact?.firstname }} {{ agreementData?.contact?.lastname }}</strong>
                </div>
            </div>

            <!-- Teleport target for SignatureSection -->
            <Teleport v-if="teleportTarget" :to="teleportTarget">
                <SignatureSection 
                    :contacts="agreementData?.contacts"
                    :activeContactId="agreementData?.active_contact_id"
                    @signed="handleSigned"
                />
            </Teleport>
        </div>
    </div>
  </div>
</template>
<style scoped>
/* Frappe Default Print Format CSS */
:deep(.print-format) {
    color: #333;
    font-size: 13px;
    line-height: 1.6;
}

:deep(.section-break) {
    padding: 15px 0;
}

:deep(.section-head) {
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 15px;
    border-bottom: 2px solid #333;
    padding-bottom: 5px;
    color: #000;
}

:deep(.field-label) {
    font-size: 11px;
    color: #777;
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: bold;
}

:deep(.field-value) {
    min-height: 18px;
}

:deep(.row) {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -15px;
}

:deep(.col-xs-6) {
    width: 50%;
    padding: 0 15px;
    box-sizing: border-box;
}

:deep(.col-xs-12) {
    width: 100%;
    padding: 0 15px;
    box-sizing: border-box;
}

:deep(.mt-4) { margin-top: 1rem; }
:deep(.mt-3) { margin-top: 0.75rem; }
:deep(.mt-2) { margin-top: 0.5rem; }

:deep(p) { margin-bottom: 16px; }
:deep(h1), :deep(h2), :deep(h3) { margin-top: 24px; margin-bottom: 12px; font-weight: bold; }
</style>
