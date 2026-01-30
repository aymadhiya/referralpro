<script setup>
import Sidebar from '@/components/Sidebar.vue'
</script>

<template>
  <div class="flex h-screen bg-surface-50 dark:bg-surface-900 font-sans overflow-hidden">
    <Sidebar />
    <main class="flex-1 overflow-y-auto">
      <router-view></router-view>
    </main>
  </div>
</template>
