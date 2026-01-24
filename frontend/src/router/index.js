import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/agency',
      children: [
        {
          path: 'login',
          name: 'AgencyLogin',
          component: () => import('@/pages/agency/Login.vue'),
        },
        {
          path: 'signup',
          name: 'AgencySignup',
          component: () => import('@/pages/agency/Signup.vue'),
        },
        {
          path: '',
          component: () => import('@/layouts/AgencyLayout.vue'),
          children: [
            {
              path: 'dashboard',
              name: 'AgencyDashboard',
              component: () => import('@/pages/agency/Dashboard.vue'),
            },
            {
              path: 'referrals',
              name: 'AgencyReferrals',
              component: () => import('@/pages/agency/ReferralLeads.vue'),
            },
            {
              path: 'partners',
              name: 'AgencyPartners',
              component: () => import('@/pages/agency/Partners.vue'),
            },
            {
              path: 'transactions',
              name: 'AgencyTransactions',
              component: () => import('@/pages/agency/Transactions.vue'),
            },
            {
              path: 'commissions',
              name: 'AgencyCommissions',
              component: () => import('@/pages/agency/Commissions.vue'),
            },
            {
              path: 'agreements',
              name: 'AgencyAgreements',
              component: () => import('@/pages/agency/Agreements.vue'),
            },
            {
              path: 'agreements/builder/:id',
              name: 'AgreementBuilder',
              component: () => import('@/pages/agency/AgreementBuilder.vue'),
            },
            {
              path: 'templates',
              name: 'AgencyTemplates',
              component: () => import('@/pages/agency/EmailTemplates.vue'),
            },
            {
              path: 'templates/edit/:id',
              name: 'EmailTemplateEditor',
              component: () => import('@/pages/agency/EmailTemplateEditor.vue'),
            },
            {
              path: 'settings',
              name: 'AgencySettings',
              component: () => import('@/pages/agency/Settings.vue'),
            },
          ]
        },
      ],
    },
    {
      path: '/partner',
      children: [
        {
          path: 'login',
          name: 'ReferralPartnerLogin',
          component: () => import('@/pages/partner/Login.vue'),
        },
      ],
    },
    {
      path: '/',
      redirect: '/agency/login',
    },
  ],
})

export default router
