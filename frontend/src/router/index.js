import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '../store/session'

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
          meta: { requiresAuth: true },
          component: () => import('@/layouts/AgencyLayout.vue'),
          children: [
            {
              path: 'dashboard',
              name: 'AgencyDashboard',
              meta: { title: 'Dashboard' },
              component: () => import('@/pages/agency/Dashboard.vue'),
            },
            {
              path: 'referrals',
              name: 'AgencyReferrals',
              meta: { title: 'Referral Leads' },
              component: () => import('@/pages/agency/ReferralLeads.vue'),
            },
            {
              path: 'referrals/:id',
              name: 'AgencyReferralDetails',
              meta: { title: 'Lead Details' },
              component: () => import('@/pages/agency/ReferralLeadDetails.vue'),
            },
            {
              path: 'partners',
              name: 'AgencyPartners',
              meta: { title: 'Partners' },
              component: () => import('@/pages/agency/Partners.vue'),
            },
            {
              path: 'transactions',
              name: 'AgencyTransactions',
              meta: { title: 'Transactions' },
              component: () => import('@/pages/agency/Transactions.vue'),
            },
            {
              path: 'commissions',
              name: 'AgencyCommissions',
              meta: { title: 'Commission Rules' },
              component: () => import('@/pages/agency/Commissions.vue'),
            },
            {
              path: 'agreements',
              name: 'AgencyAgreements',
              meta: { title: 'Agreements' },
              component: () => import('@/pages/agency/Agreements.vue'),
            },
            {
              path: 'agreements/builder/:id',
              name: 'AgreementBuilder',
              meta: { title: 'Agreement Builder' },
              component: () => import('@/pages/agency/AgreementBuilder.vue'),
            },
            {
              path: 'templates',
              name: 'AgencyTemplates',
              meta: { title: 'Email Templates' },
              component: () => import('@/pages/agency/EmailTemplates.vue'),
            },
            {
              path: 'templates/edit/:id',
              name: 'EmailTemplateEditor',
              meta: { title: 'Edit Template' },
              component: () => import('@/pages/agency/EmailTemplateEditor.vue'),
            },
            {
              path: 'settings',
              meta: { title: 'Settings' },
              component: () => import('@/pages/agency/Settings.vue'),
            },
            {
              path: 'configuration/labels',
              name: 'AgencyLabelConfig',
              meta: { title: 'Label Configuration' },
              component: () => import('@/pages/agency/AgencyLabelConfig.vue'),
            },
            {
              path: 'configuration/commission-plan',
              name: 'AgencyCommissionPlan',
              meta: { title: 'Commission Plan' },
              component: () => import('@/pages/agency/CommissionPlan.vue'),
            },
            {
              path: 'configuration/lead-fields',
              name: 'AgencyLeadFieldConfig',
              meta: { title: 'Lead Fields' },
              component: () => import('@/pages/agency/LeadFieldConfig.vue'),
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
          meta: { title: 'Partner Login' },
          component: () => import('@/pages/partner/Login.vue'),
        },
        {
          path: 'signup',
          name: 'ReferralPartnerSignup',
          meta: { title: 'Partner Signup' },
          component: () => import('@/pages/partner/Signup.vue'),
        },
        {
          path: '',
          meta: { requiresAuth: true },
          component: () => import('@/layouts/PartnerLayout.vue'),
          children: [
            {
              path: 'dashboard',
              name: 'ReferralPartnerDashboard',
              meta: { title: 'Dashboard' },
              component: () => import('@/pages/partner/Dashboard.vue'),
            },
            {
              path: 'leads',
              name: 'ReferralPartnerLeads',
              meta: { title: 'My Referrals' },
              component: () => import('@/pages/partner/Leads.vue'),
            },
            {
              path: 'leads/:id',
              name: 'ReferralPartnerLeadDetails',
              meta: { title: 'Referral Details' },
              component: () => import('@/pages/partner/LeadDetails.vue'),
            },
            {
              path: 'leads/add',
              name: 'ReferralPartnerAddLead',
              meta: { title: 'Submit Referral' },
              component: () => import('@/pages/partner/AddLead.vue'),
            },
            {
              path: 'faq',
              name: 'ReferralPartnerFAQ',
              meta: { title: 'FAQ' },
              component: () => import('@/pages/partner/FAQ.vue'),
            },
            {
              path: 'contact-us',
              name: 'ReferralPartnerContactUs',
              meta: { title: 'Contact Us' },
              component: () => import('@/pages/partner/ContactUs.vue'),
            },
            {
              path: 'profile',
              name: 'ReferralPartnerProfile',
              meta: { title: 'My Profile' },
              component: () => import('@/pages/partner/Profile.vue'),
            },
            {
              path: 'transactions',
              name: 'ReferralPartnerTransactions',
              meta: { title: 'Earnings & Payouts' },
              component: () => import('@/pages/partner/Transactions.vue'),
            },
          ]
        },
        {
          path: 'setup-directors',
          name: 'PartnerSetupDirectors',
          meta: { requiresAuth: true },
          component: () => import('@/pages/partner/SetupDirectors.vue'),
        },
        {
          path: 'verification-pending',
          name: 'ReferralPartnerVerificationPending',
          meta: { requiresAuth: true },
          component: () => import('@/pages/partner/VerificationPending.vue'),
        },
        {
          path: 'sign-agreement/:id',
          name: 'SignAgreement',
          meta: { requiresAuth: false },
          component: () => import('@/pages/public/SignAgreement.vue'),
        },
      ],
    },
    {
      path: '/',
      redirect: '/agency/login',
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const sessionStore = useSessionStore()
  const isLoggedIn = sessionStore.isLoggedIn

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      if (to.path.startsWith('/partner')) {
        next({ name: 'ReferralPartnerLogin', query: { from: to.fullPath } })
      } else {
        next({ name: 'AgencyLogin', query: { from: to.fullPath } })
      }
      return
    }

    if (!sessionStore.userInfo) {
      await sessionStore.getUserInfo()
    }

    // Role Enforcement: Check if user has access to the requested portal
    if (to.path.startsWith('/agency') && !sessionStore.userInfo.is_agency_user) {
      // Not an agency user, redirect
      if (sessionStore.userInfo.is_partner_user) {
        next({ name: 'ReferralPartnerDashboard' })
      } else {
        // Neither? Logout or error.
        next({ name: 'AgencyLogin' }) // effectively logout if session invalid for any portal
      }
      return
    }

    if (to.path.startsWith('/partner') && !sessionStore.userInfo.is_partner_user) {
      // Not a partner user, redirect
      if (sessionStore.userInfo.is_agency_user) {
        next({ name: 'AgencyDashboard' })
      } else {
        next({ name: 'ReferralPartnerLogin' })
      }
      return
    }

    // Onboarding Logic for Partners
    if (isLoggedIn && (sessionStore.account_type === 'Referral Partner' || sessionStore.account_type === 'Partner' || sessionStore.userInfo.is_partner_user)) {

      const status = sessionStore.doc ? sessionStore.doc.onboarding_status : 'Completed'

      // Allow access to setup pages based on status
      if (status === 'Pending Director Setup') {
        if (to.name !== 'PartnerSetupDirectors') {
          next({ name: 'PartnerSetupDirectors' })
          return
        }
      } else if (status === 'Pending Agreement') {
        if (to.name !== 'ReferralPartnerVerificationPending') {
          next({ name: 'ReferralPartnerVerificationPending' })
          return
        }
      }

      if (status == 'Completed' && (to.name == 'ReferralPartnerVerificationPending' || to.name == 'PartnerSetupDirectors')) {
        next({ name: 'ReferralPartnerDashboard' })
        return
      }
      // If Completed, they can go anywhere (except maybe back to setup pages? strictly speaking not blocked but usually unnecessary)
    }
  }

  // Redirect to dashboard if already logged in and visiting login pages
  const loginRoutes = ['AgencyLogin', 'ReferralPartnerLogin', 'AgencySignup']
  if (loginRoutes.includes(to.name) && isLoggedIn) {
    if (!sessionStore.userInfo) {
      await sessionStore.getUserInfo()
    }

    // Redirect based on intent (login page visited) and capability
    if (to.name === 'AgencyLogin') {
      if (sessionStore.userInfo.is_agency_user) {
        next({ name: 'AgencyDashboard' })
        return
      } else if (sessionStore.userInfo.is_partner_user) {
        next({ name: 'ReferralPartnerDashboard' })
        return
      }
    } else if (to.name === 'ReferralPartnerLogin') {
      if (sessionStore.userInfo.is_partner_user) {
        next({ name: 'ReferralPartnerDashboard' })
        return
      } else if (sessionStore.userInfo.is_agency_user) {
        next({ name: 'AgencyDashboard' })
        return
      }
    }

    // Fallback if generic route
    if (sessionStore.userInfo.is_agency_user) {
      next({ name: 'AgencyDashboard' })
    } else {
      next({ name: 'ReferralPartnerDashboard' })
    }
    return
  }

  next()
})

export default router
