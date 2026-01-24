import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config';
import { MyPreset } from '@/utils/preset.js'
import { setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'
import VueApexCharts from "vue3-apexcharts";


import App from './App.vue'
import router from './router'
import { FrappeUI } from 'frappe-ui'

import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

import './main.css'

const app = createApp(App)
setConfig('resourceFetcher', frappeRequest)
app.component('InputText', InputText)
app.component('Button', Button)

app.use(VueApexCharts)
app.use(createPinia())
app.use(router)
app.use(FrappeUI)
app.use(PrimeVue, {
    theme: {
        preset: MyPreset,
        darkModeSelector: "[data-theme='dark']",
        options: {
            cssLayer: {
                name: 'primevue',
                order: 'tailwind-base, primevue, tailwind-utilities'
            }
        }
    }
});

app.mount('#app')
