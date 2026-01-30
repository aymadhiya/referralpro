<script setup>
import { ref, watch, onMounted } from 'vue'
import SignaturePad from 'signature_pad'
import { Eraser, Check, User, Clock, FileCheck } from 'lucide-vue-next'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import FileUpload from 'primevue/fileupload'

const props = defineProps({
    contacts: {
        type: Array,
        default: () => []
    },
    activeContactId: {
        type: String,
        required: true
    }
})

const emit = defineEmits(['signed'])

const showSignatureModal = ref(false)
const signaturePad = ref(null)
const canvasRef = ref(null)
const activeTab = ref(0)
const signatureData = ref(null) // Base64 string
const submitting = ref(false)

// Initialize Signature Pad
const initPad = () => {
    if (canvasRef.value) {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvasRef.value.width = canvasRef.value.offsetWidth * ratio;
        canvasRef.value.height = canvasRef.value.offsetHeight * ratio;
        canvasRef.value.getContext("2d").scale(ratio, ratio);

        signaturePad.value = new SignaturePad(canvasRef.value, {
             backgroundColor: 'rgb(255, 255, 255)',
             penColor: 'rgb(0, 0, 0)'
        })
    }
}

watch(showSignatureModal, (val) => {
    if (val && activeTab.value === 0) {
        setTimeout(initPad, 100)
    }
})

const clearPad = () => {
    signaturePad.value?.clear()
    signatureData.value = null
}

const handleUpload = (event) => {
    const file = event.files[0]
    if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
            signatureData.value = e.target.result
        }
        reader.readAsDataURL(file)
    }
}

const confirmSignature = () => {
    if (activeTab.value === 0) {
        if (signaturePad.value?.isEmpty()) {
            alert("Please sign before saving.")
            return
        }
        signatureData.value = signaturePad.value.toDataURL()
    } else {
         if (!signatureData.value) {
             alert("Please upload a signature image.")
             return
         }
    }
    showSignatureModal.value = false
    handleSubmit()
}

const handleSubmit = () => {
    if(!signatureData.value) {
        alert("Please provide a signature.")
        return
    }

    submitting.value = true
    emit('signed', {
        signature_data: signatureData.value
        // Details removed as they are now read-only
    })
}

const getContactFullName = (c) => `${c.firstname} ${c.lastname || ''}`

</script>

<template>
    <div class="print-format">
        <div v-for="(contact, index) in contacts" :key="contact.name" class="director-block section-break">
            <div class="section-head">Director {{ index + 1 }}</div>
            
            <!-- Row 1: Contact Info (Two Columns) -->
            <div class="row info-row">
                <div class="col-xs-6">
                    <div class="field-label">Name</div>
                    <div class="field-value font-bold">{{ getContactFullName(contact) }}</div>
                </div>
                <div class="col-xs-6">
                    <div class="field-label">Email & Phone</div>
                    <div class="field-value">{{ contact.email }}</div>
                    <div class="field-value text-xs">{{ contact.phone || '' }}</div>
                </div>
            </div>

            <!-- Row 2: Signature & Date -->
            <div class="row signature-row mt-4">
                <div class="col-xs-6">
                    <div class="field-label">Signature</div>
                    <div class="signature-box mt-2">
                        <div v-if="contact.signed" class="signature-display">
                            <img v-if="contact.signature_image" :src="contact.signature_image" alt="Signature" style="max-height: 50px;" />
                        </div>
                        <div v-else-if="contact.name === activeContactId">
                            <Button 
                                @click="showSignatureModal = true" 
                                label="Sign Here" 
                                class="p-button-secondary p-button-sm p-button-outlined"
                                :loading="submitting"
                            />
                        </div>
                        <div v-else class="status-pending italic text-muted">
                            Pending Signature
                        </div>
                    </div>
                </div>
                <div class="col-xs-6">
                    <div class="field-label">Sign Date</div>
                    <div class="date-box mt-3">
                        <span v-if="contact.signed" class="font-bold underline">{{ contact.signed_date }}</span>
                        <span v-else class="date-placeholder">____________________</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Signature Dialog -->
        <Dialog v-model:visible="showSignatureModal" modal header="Electronic Signature" :style="{ width: '450px' }" class="signature-dialog">
             <TabView v-model:activeIndex="activeTab">
                <TabPanel header="Draw">
                    <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; position: relative; background: #fafafa;">
                         <canvas ref="canvasRef" class="w-full h-48 touch-none cursor-crosshair"></canvas>
                         <Button 
                            icon="pi pi-eraser"
                            text
                            severity="secondary"
                            @click="clearPad"
                            class="!absolute !top-2 !right-2 !p-1 !h-8 !w-8"
                        />
                    </div>
                </TabPanel>
                <TabPanel header="Upload">
                     <div style="height: 192px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed #ddd; border-radius: 8px; background: #fafafa;">
                        <FileUpload 
                            mode="basic" 
                            accept="image/*" 
                            :maxFileSize="1000000" 
                            @select="handleUpload" 
                            customUpload
                            auto
                            chooseLabel="Browse Image"
                            class="p-button-outlined p-button-sm"
                        />
                         <p style="font-size: 10px; color: #888; margin-top: 8px; font-weight: bold;">MAX 1MB. PNG/JPG</p>
                         <img v-if="signatureData && activeTab === 1" :src="signatureData" style="margin-top: 16px; height: 64px; object-fit: contain;" />
                    </div>
                </TabPanel>
             </TabView>

            <template #footer>
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <p style="font-size: 10px; color: #888; text-align: left; max-width: 200px; line-height: 1.2;">
                        Confirming this signature constitutes a legally binding electronic signature.
                    </p>
                    <div style="display: flex; gap: 8px;">
                        <Button label="Cancel" text class="p-button-sm" @click="showSignatureModal = false" />
                        <Button label="Confirm" icon="pi pi-check" class="p-button-sm p-button-success" @click="confirmSignature" />
                    </div>
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.print-format {
    color: #333;
    font-size: 13px;
}

.director-block {
    margin-bottom: 40px;
    page-break-inside: avoid;
}

.section-head {
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 15px;
    border-bottom: 2px solid #333;
    padding-bottom: 5px;
    color: #000;
}

.field-label {
    font-size: 11px;
    color: #777;
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: bold;
}

.field-value {
    min-height: 18px;
}

.font-bold { font-weight: bold; }
.italic { font-style: italic; }
.text-muted { color: #888; }
.underline { text-decoration: underline; }

.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -15px;
}

.col-xs-6 {
    width: 50%;
    padding: 0 15px;
    box-sizing: border-box;
}

.mt-4 { margin-top: 1rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-2 { margin-top: 0.5rem; }

.date-placeholder {
    color: #ccc;
    font-weight: normal;
}

.signature-box {
    min-height: 60px;
    display: flex;
    align-items: center;
}

.status-pending {
    font-size: 12px;
}

:deep(.p-button-sm) {
    padding: 0.35rem 0.75rem;
    font-size: 0.8rem;
}
</style>


