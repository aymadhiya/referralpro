<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  LayoutDashboard, 
  Send, 
  Users, 
  CreditCard, 
  FileText, 
  ShieldCheck, 
  Mail, 
  Settings, 
  LogOut,
  Building2
} from 'lucide-vue-next'
import { useSessionStore } from '../store/session'
import { ref } from 'vue'
import Button from 'primevue/button'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/agency/dashboard' },
  { name: 'Referral Leads', icon: Send, path: '/agency/referrals' },
  { name: 'Partners', icon: Users, path: '/agency/partners' },
  { name: 'Transactions', icon: CreditCard, path: '/agency/transactions' },
]

const configNavigation = [
  { name: 'Agreements', icon: ShieldCheck, path: '/agency/agreements' },
  { name: 'Email Templates', icon: Mail, path: '/agency/templates' },
  { name: 'Lead Status', icon: FileText, path: '/agency/configuration/labels' },
  { name: 'Lead Fields', icon: FileText, path: '/agency/configuration/lead-fields' },
  { name: 'Commission Plan', icon: FileText, path: '/agency/configuration/commission-plan' },
  { name: 'Settings', icon: Settings, path: '/agency/settings' },
]

const isActive = (path) => route.path === path

const handleLogout = async () => {
    await sessionStore.logout()
}

const orgDetails = computed(() => {
    return sessionStore.organization || {}
})
</script>

<template>
  <div class="h-screen w-64 bg-[#0F172A] flex flex-col text-white flex-shrink-0">
    <!-- Brand -->
    <div class="p-3">
      <div class="flex items-center gap-3 mb-6">
        <div v-if="orgDetails.logo" class="w-8 h-8 flex items-center justify-center">
            <img 
                :src="orgDetails.logo" 
                alt="Logo" 
                class="w-full h-full object-contain"
            />
        </div>
        <div v-else class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <span class="font-bold text-white">{{ orgDetails.organization_name ? orgDetails.organization_name.charAt(0) : 'R' }}</span>
        </div>
        <div>
            <div class="font-bold text-lg leading-tight truncate max-w-[180px]" :title="orgDetails.organization_name">{{ orgDetails.organization_name || 'Referral Portal' }}</div>
            <p class="text-[10px] text-slate-400 tracking-wider">PORTAL</p>
        </div>
      </div>
      
      <!-- Role Selector -->
      <div class="bg-slate-800/50 rounded-lg p-3 flex items-center justify-between cursor-pointer hover:bg-slate-800 transition-colors border border-slate-700/50">
        <span class="text-xs font-semibold text-slate-300">OWNER / ADMIN</span>
        <div class="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 space-y-1 overflow-y-auto custom-scrollbar">
      <router-link
        v-for="item in navigation"
        :key="item.name"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group"
        :class="[
          isActive(item.path) 
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
            : 'text-slate-400 hover:text-white hover:bg-slate-800'
        ]"
      >
        <component 
            :is="item.icon" 
            :size="18" 
            :class="isActive(item.path) ? 'text-white' : 'text-slate-400 group-hover:text-white'"
        />
        {{ item.name }}
        <span v-if="isActive(item.path)" class="ml-auto">
            <svg width="6" height="10" viewBox="0 0 6 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 9L5 5L1 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </span>
      </router-link>

      <!-- Configuration Section -->
      <div class="pt-4 pb-2">
        <p class="px-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Configuration</p>
      </div>
      
      <router-link
        v-for="item in configNavigation"
        :key="item.name"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group"
        :class="[
          isActive(item.path) 
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
            : 'text-slate-400 hover:text-white hover:bg-slate-800'
        ]"
      >
        <component 
            :is="item.icon" 
            :size="18" 
            :class="isActive(item.path) ? 'text-white' : 'text-slate-400 group-hover:text-white'"
        />
        {{ item.name }}
        <span v-if="isActive(item.path)" class="ml-auto">
            <svg width="6" height="10" viewBox="0 0 6 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 9L5 5L1 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </span>
      </router-link>
    </nav>

    <!-- Context / Footer -->
    <div class="p-4 border-t border-slate-800">
        <div class="bg-slate-900 rounded-xl p-4 border border-slate-800">
            <p class="text-[10px] font-bold text-slate-500 uppercase mb-3">Context</p>
            <Button 
                label="Switch Agency"
                icon="pi pi-building"
                text
                severity="secondary"
                class="w-full !px-3 !py-2 !text-xs font-semibold mb-4 border border-slate-700 hover:!bg-slate-800"
            />
            
            <Button 
                @click="handleLogout"
                label="Sign Out"
                icon="pi pi-power-off"
                text
                class="!px-1 !text-xs font-medium !text-slate-400 hover:!text-white"
            />
        </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}
</style>
