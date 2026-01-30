<script setup>
import { onMounted, watch, computed } from 'vue'
import { useSessionStore } from './store/session'
import { useRoute } from 'vue-router'
import Toast from 'primevue/toast'
import { applyBrandColor } from '@/utils/branding'

const sessionStore = useSessionStore()
const route = useRoute()

// Dynamic Title & Favicon Logic
const updateHead = () => {
    const org = sessionStore.organization
    const orgName = org?.organization_name || 'Referral Portal'
    const pageTitle = route.meta.title || route.name || ''
    
    // Update Title
    // If page title is present, format as "Page Title - Org Name"
    // Otherwise just "Org Name"
    if (pageTitle && pageTitle !== 'AgencyDashboard' && pageTitle !== 'ReferralPartnerDashboard') { // specific check or generic?
        // Let's use a cleaner approach. If route has a friendly name or meta title.
        // We might want to map route names to friendly titles if meta isn't set.
        // For now, let's assume route.name is a bit raw, maybe rely on meta.title being added or just org name if not.
        if (route.meta.title) {
            document.title = `${route.meta.title} - ${orgName}`
        } else {
             document.title = orgName
        }
    } else {
        document.title = orgName
    }

    // Update Favicon
    if (org?.logo) {
        const link = document.querySelector("link[rel~='icon']")
        if (link) {
            link.href = org.logo
        } else {
             const newLink = document.createElement('link')
             newLink.rel = 'icon'
             newLink.href = org.logo
             document.head.appendChild(newLink)
        }
    }
}

// Watchers
watch(() => sessionStore.organization, (org) => {
    if (org) {
        applyTheme(org.theme_mode)
        if (org.brand_color) {
            applyBrandColor(org.brand_color)
        }
        updateHead()
    }
}, { deep: true })

watch(() => route.path, () => {
    updateHead()
})

const applyTheme = (mode) => {
    const html = document.documentElement
    if (mode === 'Dark') {
        html.classList.add('dark')
    } else if (mode === 'Light') {
        html.classList.remove('dark')
    } else {
        // System
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            html.classList.add('dark')
        } else {
            html.classList.remove('dark')
        }
    }
}

onMounted(async () => {
    if (sessionStore.isLoggedIn) {
        await sessionStore.getOrganizationDetails()
    }
})
</script>

<template>
  <router-view />
  <Toast />
</template>


<style scoped></style>
