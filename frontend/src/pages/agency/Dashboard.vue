<script setup>
import { ref, computed } from 'vue'
import { Users, Send, DollarSign, ShieldCheck, TrendingUp, ArrowUpRight } from 'lucide-vue-next'

// Mock Data
const leadData = [
  { name: 'Jan', value: 4 },
  { name: 'Feb', value: 7 },
  { name: 'Mar', value: 5 },
  { name: 'Apr', value: 12 },
  { name: 'May', value: 18 },
  { name: 'Jun', value: 15 },
  { name: 'Jul', value: 24 },
]

const commissionData = [
    { name: 'Jan', amount: 1200 },
    { name: 'Feb', amount: 2100 },
    { name: 'Mar', amount: 1500 },
    { name: 'Apr', amount: 3200 },
    { name: 'May', amount: 4500 },
    { name: 'Jun', amount: 3800 },
    { name: 'Jul', amount: 6000 },
]

// Determine Role (Mocking role for now as per React props)
// In real app, get this from store/auth
const role = ref('AGENCY_ADMIN') 
const isAgency = computed(() => role.value === 'AGENCY_ADMIN')

// Chart Options
const areaChartOptions = {
  chart: {
    type: 'area',
    toolbar: { show: false },
    fontFamily: 'inherit',
    zoom: { enabled: false }
  },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#3B82F6'] },
  xaxis: {
    categories: leadData.map(d => d.name),
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
  tooltip: {
    theme: 'light',
    y: { formatter: (val) => val }
  }
}

const areaChartSeries = [{
  name: 'Leads',
  data: leadData.map(d => d.value)
}]

const barChartOptions = {
  chart: {
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'inherit'
  },
  plotOptions: {
    bar: {
      borderRadius: 4,
      columnWidth: '60%',
    }
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: commissionData.map(d => d.name),
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
}

const barChartSeries = [{
  name: 'Commission',
  data: commissionData.map(d => d.amount)
}]

</script>

<template>
  <div class="space-y-8 p-6 md:p-10 max-w-[1600px] mx-auto">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
          <h1 class="text-3xl font-bold text-slate-900 tracking-tight">
          {{ isAgency ? 'Agency Overview' : 'Partner Dashboard' }}
          </h1>
          <p class="text-slate-500 mt-1">Welcome back, here's what's happening today.</p>
      </div>
      <button v-if="isAgency" class="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-lg shadow-slate-200 flex items-center gap-2 cursor-pointer">
          <Users :size="18" />
          Invite Partner
      </button>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <!-- Stat Card 1 -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-blue-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-500">{{ isAgency ? "Total Referrals" : "My Referrals" }}</p>
                <h3 class="text-3xl font-bold text-slate-900 mt-2 tracking-tight">48</h3>
                <div class="flex items-center gap-1 mt-2 text-xs font-bold text-emerald-600 bg-emerald-50 w-fit px-2 py-1 rounded-full">
                    <TrendingUp :size="12" />
                    +12% vs last month
                </div>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
                <Send :size="20" />
            </div>
        </div>
      </div>

      <!-- Stat Card 2 -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-purple-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-500">{{ isAgency ? "Active Partners" : "Current Tier" }}</p>
                <h3 class="text-3xl font-bold text-slate-900 mt-2 tracking-tight">{{ isAgency ? "12" : "Gold" }}</h3>
                 <div class="flex items-center gap-1 mt-2 text-xs font-bold text-emerald-600 bg-emerald-50 w-fit px-2 py-1 rounded-full">
                    <TrendingUp :size="12" />
                    {{ isAgency ? "+2 new" : "Top 10%" }}
                </div>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-purple-500 to-purple-600">
                <Users :size="20" />
            </div>
        </div>
      </div>

      <!-- Stat Card 3 -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-emerald-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-500">{{ isAgency ? "Commissions Paid" : "Total Earnings" }}</p>
                <h3 class="text-3xl font-bold text-slate-900 mt-2 tracking-tight">$15,700</h3>
            </div>
            <div class="p-3 rounded-xl text-white shadow-lg bg-gradient-to-br from-emerald-500 to-emerald-600">
                <DollarSign :size="20" />
            </div>
        </div>
      </div>

       <!-- Stat Card 4 -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-24 rounded-full opacity-5 translate-x-8 -translate-y-8 transition-transform group-hover:scale-110 bg-orange-500"></div>
        <div class="relative z-10 flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-500">{{ isAgency ? "Pending Agreements" : "Compliance" }}</p>
                <h3 class="text-3xl font-bold text-slate-900 mt-2 tracking-tight">{{ isAgency ? "3" : "Verified" }}</h3>
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
      <div class="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <div class="flex justify-between items-center mb-6">
           <h2 class="text-lg font-bold text-slate-900">Lead Volume Trend</h2>
           <select class="bg-slate-50 border-none text-xs font-semibold text-slate-600 rounded-lg px-3 py-1.5 focus:ring-0 cursor-pointer hover:bg-slate-100 outline-none">
              <option>Last 6 Months</option>
              <option>Last Year</option>
           </select>
        </div>
        <div class="h-80 w-full">
           <apexchart type="area" height="100%" :options="areaChartOptions" :series="areaChartSeries"></apexchart>
        </div>
      </div>

      <!-- Bar Chart Card -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col">
           <h2 class="text-lg font-bold text-slate-900 mb-6">Financial Performance</h2>
           <div class="h-48 w-full mb-6 flex-1">
              <apexchart type="bar" height="100%" :options="barChartOptions" :series="barChartSeries"></apexchart>
           </div>
           
           <div class="space-y-4 mt-auto">
               <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                   <div class="flex items-center gap-3">
                       <div class="p-2 bg-emerald-100 text-emerald-600 rounded-lg">
                           <TrendingUp :size="16" />
                       </div>
                       <div>
                           <p class="text-xs font-semibold text-slate-500">Avg. Commission</p>
                           <p class="text-sm font-bold text-slate-900">$1,250</p>
                       </div>
                   </div>
                   <ArrowUpRight :size="16" class="text-emerald-500" />
               </div>
               <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                   <div class="flex items-center gap-3">
                       <div class="p-2 bg-blue-100 text-blue-600 rounded-lg">
                           <Send :size="16" />
                       </div>
                       <div>
                           <p class="text-xs font-semibold text-slate-500">Conversion Rate</p>
                           <p class="text-sm font-bold text-slate-900">24%</p>
                       </div>
                   </div>
                    <ArrowUpRight :size="16" class="text-blue-500" />
               </div>
           </div>
      </div>
    </div>
  </div>
</template>
