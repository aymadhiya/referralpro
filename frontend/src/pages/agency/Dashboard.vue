<script setup>
import { ref, computed, onMounted } from 'vue'
import { Users, Send, DollarSign, ShieldCheck, TrendingUp, ArrowUpRight, Link } from 'lucide-vue-next'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../../store/session'

const router = useRouter()
const sessionStore = useSessionStore()

// State
const stats = ref({
    total_referrals: 0,
    referral_growth: 0,
    active_partners: 0, 
    partners_growth: 0,
    total_commission_paid: 0,
    pending_agreements: 0,
    lead_chart: { labels: [], data: [] },
    financial_chart: { labels: [], data: [] },
    recent_transactions: [],
    avg_commission: 0,
    conversion_rate: 0
})

// Data Resource
const dashboardResource = createResource({
    url: 'referralpro.api.agency.dashboard.get_dashboard_stats',
    onSuccess: (data) => {
        if (data) {
            stats.value = data
            updateCharts()
        }
    }
})

// Current user role check
const isAgency = computed(() => sessionStore.userInfo?.is_agency_user)

onMounted(() => {
    if (isAgency.value) {
        dashboardResource.fetch()
    }
})

// Chart Configuration
const areaChartOptions = ref({
  chart: {
    type: 'area',
    toolbar: { show: false },
    fontFamily: 'inherit',
    zoom: { enabled: false }
  },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#3B82F6'] },
  xaxis: {
    categories: [],
    axisBorder: { show: false },
    axisTicks: { show: false },
    labels: { style: { colors: '#64748B', fontSize: '12px' } }
  },
  yaxis: {
    show: true,
    labels: { style: { colors: '#64748B', fontSize: '12px' } }
  },
  grid: {
    borderColor: '#F1F5F9',
    strokeDashArray: 3,
    xaxis: { lines: { show: true } },   
    yaxis: { lines: { show: true } },
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.4,
      opacityTo: 0.05,
      stops: [0, 100]
    }
  },
  colors: ['#3B82F6'],
  tooltip: { theme: 'light' }
})

const areaChartSeries = ref([{ name: 'Leads', data: [] }])

const barChartOptions = ref({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'inherit'
  },
  plotOptions: {
    bar: { borderRadius: 4, columnWidth: '60%' }
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: [],
    axisBorder: { show: false },
    axisTicks: { show: false },
    labels: { style: { colors: '#64748B', fontSize: '12px' } }
  },
  yaxis: { show: false },
  grid: { show: false },
  colors: ['#10B981'],
  tooltip: {
    theme: 'light',
    y: { formatter: (val) => '$' + val }
  }
})

const barChartSeries = ref([{ name: 'Commission', data: [] }])

const updateCharts = () => {
    // Update Lead Chart
    areaChartOptions.value = {
        ...areaChartOptions.value,
        xaxis: { ...areaChartOptions.value.xaxis, categories: stats.value.lead_chart.labels }
    }
    areaChartSeries.value = [{ name: 'Leads', data: stats.value.lead_chart.data }]
    
    // Update Financial Chart
    barChartOptions.value = {
        ...barChartOptions.value,
        xaxis: { ...barChartOptions.value.xaxis, categories: stats.value.financial_chart.labels }
    }
    barChartSeries.value = [{ name: 'Commission', data: stats.value.financial_chart.data }]
}

const navigateToInvite = () => {
    router.push('/agency/partners?invite=true')
}

const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(val)
}
</script>

<template>
  <div class="space-y-8 p-6 md:p-10 max-w-[1600px] mx-auto">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
          <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-0 tracking-tight">Agency Overview</h1>
          <p class="text-surface-500 dark:text-surface-400 mt-1">Real-time performance metrics and insights.</p>
      </div>
      <Button 
        @click="navigateToInvite" 
        label="Invite Partner"
        icon="pi pi-users"
        class="shadow-lg"
      />
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <!-- Total Referrals -->
      <div class="bg-surface-0 p-6 rounded-2xl border border-surface-100 dark:border-surface-700 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-blue-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-surface-500 dark:text-surface-400">Total Referrals</p>
                <div v-if="dashboardResource.loading" class="h-8 w-16 bg-slate-100 animate-pulse rounded mt-2"></div>
                <h3 v-else class="text-3xl font-bold text-surface-900 dark:text-surface-0 mt-2 tracking-tight">{{ stats.total_referrals }}</h3>
                
                <div class="flex items-center gap-1 mt-2 text-xs font-bold w-fit px-2 py-1 rounded-full" 
                    :class="stats.referral_growth >= 0 ? 'text-emerald-600 bg-emerald-50' : 'text-red-600 bg-red-50'">
                    <TrendingUp :size="12" />
                    {{ stats.referral_growth }}% vs last month
                </div>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
                <Send :size="20" />
            </div>
        </div>
      </div>

      <!-- Active Partners -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-purple-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-surface-500 dark:text-surface-400">Active Partners</p>
                <div v-if="dashboardResource.loading" class="h-8 w-16 bg-slate-100 animate-pulse rounded mt-2"></div>
                <h3 v-else class="text-3xl font-bold text-surface-900 dark:text-surface-0 mt-2 tracking-tight">{{ stats.active_partners }}</h3>
                 <div class="flex items-center gap-1 mt-2 text-xs font-bold text-purple-600 bg-purple-50 w-fit px-2 py-1 rounded-full">
                    <Users :size="12" />
                    {{ stats.partners_growth }} new this month
                </div>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-purple-500 to-purple-600">
                <Users :size="20" />
            </div>
        </div>
      </div>

      <!-- Commissions Paid -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-emerald-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-surface-500 dark:text-surface-400">Commissions Paid</p>
                <div v-if="dashboardResource.loading" class="h-8 w-24 bg-slate-100 animate-pulse rounded mt-2"></div>
                <h3 v-else class="text-3xl font-bold text-surface-900 dark:text-surface-0 mt-2 tracking-tight">{{ formatCurrency(stats.total_commission_paid) }}</h3>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-emerald-500 to-emerald-600">
                <DollarSign :size="20" />
            </div>
        </div>
      </div>

       <!-- Pending Agreements -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-orange-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-surface-500 dark:text-surface-400">Pending Agreements</p>
                <div v-if="dashboardResource.loading" class="h-8 w-12 bg-slate-100 animate-pulse rounded mt-2"></div>
                <h3 v-else class="text-3xl font-bold text-surface-900 dark:text-surface-0 mt-2 tracking-tight">{{ stats.pending_agreements }}</h3>
                <div v-if="stats.pending_agreements > 0" class="flex items-center gap-1 mt-2 text-xs font-bold text-orange-600 bg-orange-50 w-fit px-2 py-1 rounded-full cursor-pointer hover:bg-orange-100" @click="router.push('/agency/partners')">
                    Action Required
                </div>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-orange-500 to-orange-600">
                <ShieldCheck :size="20" />
            </div>
        </div>
      </div>
      
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Area Chart Card -->
      <div class="lg:col-span-2 bg-surface-0 p-6 rounded-2xl border border-surface-100 dark:border-surface-700 shadow-sm">
        <div class="flex justify-between items-center mb-6">
           <h2 class="text-lg font-bold text-surface-900 dark:text-surface-0">Lead Volume Trend</h2>
           <div class="text-xs font-semibold text-slate-400">Last 6 Months</div>
        </div>
        <div class="h-80 w-full relative">
           <div v-if="dashboardResource.loading" class="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                <div class="animate-spin w-8 h-8 boundary-blue-500 rounded-full border-2 border-t-transparent border-blue-600"></div>
           </div>
           <apexchart type="area" height="100%" :options="areaChartOptions" :series="areaChartSeries"></apexchart>
        </div>
      </div>

      <!-- Bar Chart Card -->
      <div class="bg-surface-0 p-6 rounded-2xl border border-surface-100 dark:border-surface-700 shadow-sm flex flex-col">
           <h2 class="text-lg font-bold text-surface-900 dark:text-surface-0 mb-6">Financial Performance</h2>
           <div class="h-48 w-full mb-6 flex-1 relative">
              <div v-if="dashboardResource.loading" class="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                    <div class="animate-spin w-8 h-8 boundary-blue-500 rounded-full border-2 border-t-transparent border-emerald-600"></div>
              </div>
              <apexchart type="bar" height="100%" :options="barChartOptions" :series="barChartSeries"></apexchart>
           </div>
           
           <div class="space-y-4 mt-auto">
               <div class="flex items-center justify-between p-3 bg-surface-50 rounded-xl">
                   <div class="flex items-center gap-3">
                       <div class="p-2 bg-emerald-100 text-emerald-600 dark:text-emerald-400 rounded-lg">
                           <TrendingUp :size="16" />
                       </div>
                       <div>
                           <p class="text-xs font-semibold text-surface-500 dark:text-surface-400">Avg. Commission</p>
                           <p class="text-sm font-bold text-surface-900 dark:text-surface-0">{{ formatCurrency(stats.avg_commission) }}</p>
                       </div>
                   </div>
                   <ArrowUpRight :size="16" class="text-emerald-500" />
               </div>
               <div class="flex items-center justify-between p-3 bg-surface-50 rounded-xl">
                   <div class="flex items-center gap-3">
                       <div class="p-2 bg-blue-100 text-blue-600 dark:text-blue-400 rounded-lg">
                           <Send :size="16" />
                       </div>
                       <div>
                           <p class="text-xs font-semibold text-surface-500 dark:text-surface-400">Conversion Rate</p>
                           <p class="text-sm font-bold text-surface-900 dark:text-surface-0">{{ stats.conversion_rate }}%</p>
                       </div>
                   </div>
                    <ArrowUpRight :size="16" class="text-blue-500" />
               </div>
           </div>
      </div>
    </div>
    
    <!-- Recent Transactions Widget -->
    <div class="bg-surface-0 p-6 rounded-2xl border border-surface-100 dark:border-surface-700 shadow-sm">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-bold text-surface-900 dark:text-surface-0">Recent Transactions</h2>
            <Button label="View All" text size="small" @click="router.push('/agency/transactions')" />
        </div>
        
        <DataTable :value="stats.recent_transactions" :loading="dashboardResource.loading" class="p-datatable-sm">
            <template #empty>
                <div class="text-slate-400 text-sm py-4">No recent transactions.</div>
            </template>
            <Column field="date" header="Date"></Column>
            <Column field="partner" header="Partner"></Column>
            <Column field="amount" header="Amount">
                 <template #body="slotProps">
                    <span class="font-bold">{{ formatCurrency(slotProps.data.amount) }}</span>
                </template>
            </Column>
            <Column field="status" header="Status">
                 <template #body="slotProps">
                    <Tag :value="slotProps.data.status" :severity="slotProps.data.status === 'Paid' ? 'success' : slotProps.data.status === 'Approved' ? 'info' : 'warning'" class="text-[10px]" />
                </template>
            </Column>
        </DataTable>
    </div>
    
  </div>
</template>
