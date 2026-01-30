<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import { 
    LayoutDashboard, 
    Users, 
    MessageSquare, 
    UserCircle, 
    LogOut, 
    ChevronDown,
    HelpCircle,
    CreditCard
} from 'lucide-vue-next'
import { useSessionStore } from '../store/session'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'

const router = useRouter()
const route = useRoute()
const sessionStore = useSessionStore()

const sidebarOpen = ref(true)
const agencies = ref([])
const selectedAgency = ref(null)

const agencyResource = createResource({
    url: 'referralpro.api.partner.partner.get_partner_organizations',
    onSuccess: (data) => {
        agencies.value = data
        if (data && data.length > 0) {
            // Check if there is a store preference or default to first
            selectedAgency.value = data[0]
        }
    }
})

const navigation = [
    { name: 'Dashboard', path: '/partner/dashboard', icon: LayoutDashboard },
    { name: 'Leads', path: '/partner/leads', icon: Users },
    { name: 'Transactions', path: '/partner/transactions', icon: CreditCard },
    { name: 'FAQ', path: '/partner/faq', icon: HelpCircle },
    { name: 'Contact Us', path: '/partner/contact-us', icon: MessageSquare },
    { name: 'Profile', path: '/partner/profile', icon: UserCircle },
]

const logout = async () => {
    await sessionStore.logout()
    router.push('/partner/login')
}

onMounted(() => {
    agencyResource.fetch()
})

const isActive = (path) => route.path === path

const onAgencyChange = (event) => {
    // Handle agency switch logic if needed (e.g., store in session/localstorage to filter data)
    console.log("Switched to agency:", event.value)
}

</script>

<template>
    <div class="flex h-screen bg-surface-50 dark:bg-surface-900 font-sans text-surface-900 dark:text-surface-0">
        <!-- Sidebar -->
        <aside 
            class="bg-surface-0 dark:bg-surface-800 border-r border-surface-200 dark:border-surface-700 flex flex-col transition-all duration-300"
            :class="sidebarOpen ? 'w-64' : 'w-20'"
        >
            <!-- Logo / Organization Switcher -->
            <div class="h-16 flex items-center justify-center border-b border-surface-200 dark:border-surface-700 px-4">
                <div v-if="sidebarOpen" class="w-full">
                    <Dropdown 
                        v-if="agencies.length > 1"
                        v-model="selectedAgency" 
                        :options="agencies" 
                        optionLabel="organization_name" 
                        class="w-full md:w-14rem" 
                        @change="onAgencyChange"
                    >
                        <template #value="slotProps">
                            <div v-if="slotProps.value" class="flex items-center gap-2">
                                <img v-if="slotProps.value.logo" :src="slotProps.value.logo" class="w-6 h-6 rounded object-cover" />
                                <div v-else class="w-6 h-6 rounded bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 font-bold text-xs">
                                    {{ slotProps.value.organization_name.charAt(0) }}
                                </div>
                                <span class="truncate">{{ slotProps.value.organization_name }}</span>
                            </div>
                            <span v-else>
                                {{ slotProps.placeholder }}
                            </span>
                        </template>
                        <template #option="slotProps">
                            <div class="flex items-center gap-2">
                                <img v-if="slotProps.option.logo" :src="slotProps.option.logo" class="w-6 h-6 rounded object-cover" />
                                <div v-else class="w-6 h-6 rounded bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 font-bold text-xs">
                                    {{ slotProps.option.organization_name.charAt(0) }}
                                </div>
                                <div>{{ slotProps.option.organization_name }}</div>
                            </div>
                        </template>
                    </Dropdown>
                    <div v-else-if="selectedAgency" class="flex items-center gap-3 px-2">
                         <img v-if="selectedAgency.logo" :src="selectedAgency.logo" class="w-8 h-8 rounded object-cover" />
                         <div v-else class="w-8 h-8 rounded bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 font-bold text-sm">
                            {{ selectedAgency.organization_name.charAt(0) }}
                        </div>
                        <span class="font-bold truncate">{{ selectedAgency.organization_name }}</span>
                    </div>
                     <div v-else class="flex items-center gap-2 animate-pulse">
                        <div class="w-8 h-8 bg-surface-200 rounded"></div>
                        <div class="h-4 w-24 bg-surface-200 rounded"></div>
                    </div>
                </div>
                <div v-else class="flex items-center justify-center">
                    <img v-if="selectedAgency && selectedAgency.logo" :src="selectedAgency.logo" class="w-8 h-8 rounded object-cover" />
                     <div v-else-if="selectedAgency" class="w-8 h-8 rounded bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 font-bold text-sm">
                        {{ selectedAgency.organization_name.charAt(0) }}
                    </div>
                    <Building2 v-else class="w-8 h-8 text-emerald-600" />
                </div>
            </div>

            <!-- Add Referral Button -->
            <div class="px-3 py-4 flex flex-col gap-2">
                <Button 
                    v-if="sidebarOpen"
                    @click="router.push('/partner/leads/add')"
                    label="Add Referral" 
                    icon="pi pi-plus" 
                    class="w-full"
                />
                <Button 
                    v-else
                    @click="router.push('/partner/leads/add')"
                    icon="pi pi-plus" 
                    class="w-full"
                />
            </div>

            <!-- Navigation -->
            <nav class="flex-1 py-2 px-3 space-y-1 overflow-y-auto">
                <router-link 
                    v-for="item in navigation" 
                    :key="item.name" 
                    :to="item.path"
                    class="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group"
                    :class="isActive(item.path) 
                        ? 'bg-primary-50 text-primary-600 font-bold' 
                        : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 font-medium'"
                >
                    <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
                    <span v-if="sidebarOpen">{{ item.name }}</span>
                </router-link>
            </nav>

            <div class="p-3 border-t border-surface-200 dark:border-surface-700">
                <Button 
                    @click="logout" 
                    label="Logout"
                    icon="pi pi-power-off"
                    text
                    severity="danger"
                    class="w-full !justify-start"
                >
                    <template v-if="!sidebarOpen" #label>
                        <span></span>
                    </template>
                </Button>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 flex flex-col h-screen overflow-hidden bg-surface-50 dark:bg-surface-900">
             <!-- Header (Mobile Toggle etc could go here) -->
             <header class="h-16 bg-surface-0 dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between px-6 shadow-sm">
                <h2 class="text-xl font-bold">{{ route.name }}</h2>
                <!-- Add User Avatar or common controls here -->
            </header>

            <div class="flex-1 overflow-auto p-6 md:p-8">
                <router-view />
            </div>
        </main>
    </div>
</template>
