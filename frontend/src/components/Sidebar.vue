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

const route = useRoute()
const router = useRouter()

const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/agency/dashboard' },
  { name: 'Referral Leads', icon: Send, path: '/agency/referrals' },
  { name: 'Partners', icon: Users, path: '/agency/partners' },
  { name: 'Transactions', icon: CreditCard, path: '/agency/transactions' },
  { name: 'Commission Plan', icon: FileText, path: '/agency/commissions' },
  { name: 'Agreements', icon: ShieldCheck, path: '/agency/agreements' },
  { name: 'Email Templates', icon: Mail, path: '/agency/templates' },
  { name: 'Settings', icon: Settings, path: '/agency/settings' },
]

const isActive = (path) => route.path === path

const handleLogout = () => {
    // Implement logout logic here
    router.push('/agency/login')
}
</script>

<template>
  <div class="h-screen w-64 bg-[#0F172A] flex flex-col text-white flex-shrink-0">
    <!-- Brand -->
    <div class="p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <span class="font-bold text-white">O</span>
        </div>
        <div>
            <h1 class="font-bold text-sm leading-tight">Oswal Marketing</h1>
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
    </nav>

    <!-- Context / Footer -->
    <div class="p-4 border-t border-slate-800">
        <div class="bg-slate-900 rounded-xl p-4 border border-slate-800">
            <p class="text-[10px] font-bold text-slate-500 uppercase mb-3">Context</p>
            <button class="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold py-2 px-3 rounded-lg flex items-center justify-center gap-2 transition-colors mb-4 border border-slate-700">
                <Building2 :size="14" />
                Switch Agency
            </button>
            
            <button 
                @click="handleLogout"
                class="flex items-center gap-2 text-slate-400 hover:text-white text-xs font-medium transition-colors pl-1"
            >
                <LogOut :size="14" />
                Sign Out
            </button>
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
