<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import Button from 'primevue/button'
import { 
    LayoutDashboard, 
    Users, 
    ArrowUpRight, 
    DollarSign, 
    Target,
    Clock,
    CheckCircle2,
    Calendar,
    ChevronRight,
    TrendingUp
} from 'lucide-vue-next'

const stats = ref([
    { name: 'Total Referrals', value: '0', icon: Target, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'Active Referrals', value: '0', icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { name: 'Pending Commissions', value: '$0.00', icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
    { name: 'Paid Commissions', value: '$0.00', icon: DollarSign, color: 'text-purple-600', bg: 'bg-purple-50' }
])

const recentReferrals = ref([])
const loading = ref(true)

onMounted(() => {
    // Initial stats and data fetch will go here
    loading.value = false
})
</script>

<template>
  <div class="p-8 max-w-7xl mx-auto space-y-10 font-sans">
    
    <!-- Welcome Header -->
    <header class="flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div class="space-y-2">
        <div class="flex items-center gap-2 text-emerald-600 font-bold text-sm tracking-wider uppercase">
            <TrendingUp :size="16" />
            <span>Growth Dashboard</span>
        </div>
        <h1 class="text-4xl font-black text-surface-900 dark:text-surface-0 tracking-tight">
          Welcome back, Partner!
        </h1>
        <p class="text-surface-500 dark:text-surface-400 font-medium text-lg lg:max-w-xl">
          Track your referrals, monitor commissions, and see your impact in real-time.
        </p>
      </div>
      
      <div class="flex items-center gap-3">
         <Button 
            icon="pi pi-calendar"
            text
            severity="secondary"
         />
         <Button 
            label="Add New Referral"
            icon="pi pi-plus"
            iconPos="right"
            @click="router.push('/partner/leads/add')"
         />
      </div>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="stat in stats" :key="stat.name" 
           class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-100 dark:border-surface-800 shadow-sm transition-all hover:translate-y-1 group">
        <div :class="[stat.bg, stat.color, 'w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:scale-105 transition-transform']">
          <component :is="stat.icon" :size="28" />
        </div>
        <p class="text-sm font-bold text-surface-500 dark:text-surface-400 uppercase tracking-widest mb-1">{{ stat.name }}</p>
        <div class="flex items-baseline gap-2">
            <h3 class="text-3xl font-black text-surface-900 dark:text-surface-0">{{ stat.value }}</h3>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Recent Referrals -->
      <div class="lg:col-span-2 space-y-6">
        <div class="flex items-center justify-between px-2">
            <h2 class="text-2xl font-black text-surface-900 dark:text-surface-0 tracking-tight">Recent Referrals</h2>
            <Button 
                label="View All"
                icon="pi pi-chevron-right"
                iconPos="right"
                text
                size="small"
            />
        </div>
        
        <div class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-100 dark:border-surface-800 shadow-sm overflow-hidden">
            <div v-if="recentReferrals.length === 0" class="p-16 text-center space-y-4">
                <div class="w-20 h-20 bg-surface-50 dark:bg-surface-800 rounded-full flex items-center justify-center mx-auto text-surface-300">
                    <Users :size="40" />
                </div>
                <h3 class="text-xl font-bold text-surface-900 dark:text-surface-0">No referrals yet</h3>
                <p class="text-surface-500 max-w-sm mx-auto">Start sharing your unique partner link to see your referrals appear here.</p>
                <Button 
                    label="Learn How It Works"
                    severity="secondary"
                    text
                />
            </div>
            <div v-else class="divide-y divide-surface-50 dark:divide-surface-800">
                <!-- Referral Rows will go here -->
            </div>
        </div>
      </div>

      <div class="space-y-8">
         <div class="bg-surface-900 text-white p-6 rounded-xl shadow-lg relative overflow-hidden group">
            <div class="absolute -right-12 -top-12 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all"></div>
            
            <h3 class="text-xl font-bold mb-6 flex items-center gap-2">
                <LayoutDashboard :size="20" class="text-emerald-400" />
                Partner Quick Link
            </h3>
            
            <p class="text-slate-400 text-sm font-medium mb-4">Share this link with your network to earn rewards:</p>
            
            <div class="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 mb-6 flex items-center justify-between gap-3 group/link">
                <Button 
                    v-if="false"
                    icon="pi pi-check"
                    severity="success"
                />
                <Button 
                    v-else
                    icon="pi pi-external-link"
                />
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-white/5 rounded-lg border border-white/5">
                    <p class="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1">Click Rate</p>
                    <p class="text-lg font-black">2.4%</p>
                </div>
                <div class="p-4 bg-white/5 rounded-lg border border-white/5">
                    <p class="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1">Conv. Rate</p>
                    <p class="text-lg font-black">0.8%</p>
                </div>
            </div>
         </div>

         <div class="bg-emerald-50 dark:bg-emerald-950/20 p-6 rounded-xl border border-emerald-100 dark:border-emerald-900/30">
            <h4 class="text-emerald-900 dark:text-emerald-400 font-black text-lg mb-2">Need assistance?</h4>
            <p class="text-emerald-700 dark:text-emerald-500 text-sm font-medium mb-6">Our partner success team is always here to help you grow your business.</p>
            <Button 
                label="Contact Support"
                text
                severity="success"
                class="w-full"
            />
         </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Optional: specific styles for dashboard grid or charts */
</style>
