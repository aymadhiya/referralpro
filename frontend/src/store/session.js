import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'
import router from '../router'

function getSessionUser() {
    let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
    let _sessionUser = cookies.get('user_id')
    return _sessionUser === 'Guest' ? null : _sessionUser
}


export const useSessionStore = defineStore('session', {
    state: () => ({
        user: getSessionUser(),
        error: false,
        success: false,
        userInfo: null,
        is_agency_user: false,
        is_partner_user: false,
        doc: null,
        organization: null
    }),

    getters: {
        isLoggedIn: (state) => !!state.user,
    },

    actions: {
        get_current_path() {
            const route = useRoute()
            const currentPath = route
            return { currentPath }
        },
        async validateUserRoles() {
            const data = createResource({
                method: 'get',
                url: 'referralpro.api.auth.validate_user_roles',
            })
            const res = await data.reload()
            return res
        },
        async getUserInfo() {
            const data = createResource({
                method: 'get',
                url: 'referralpro.api.auth.get_user_info',
            })
            const res = await data.reload()
            this.userInfo = res;
            this.is_agency_user = res?.is_agency_user || false
            this.is_partner_user = res?.is_partner_user || false
            this.doc = {
                onboarding_status: res?.onboarding_status
            }
        },
        async getOrganizationDetails() {
            const data = createResource({
                url: 'referralpro.api.agency.doc.get_list',
                params: {
                    doctype: 'Organization',
                    fields: JSON.stringify(['organization_name', 'logo', 'theme_mode', 'brand_color']),
                    page_length: 1
                }
            })
            const res = await data.fetch()
            if (res && res.length > 0) {
                this.organization = res[0]
            }
        },
        async login(email, password, redirectPath = null) {
            const data = createResource({
                method: 'post',
                url: 'referralpro.api.auth.login',
                params: {
                    usr: email,
                    pwd: password,
                },
                onSuccess: async (data) => {
                    if (data.success_key) {
                        await this.getUserInfo()
                        this.user = getSessionUser()
                    }
                    const route = redirectPath || data.default_route || '/';
                    this.error = data.message;
                    this.success = data.success_key;
                    const urlParams = new URLSearchParams(window.location.search);
                    const from = urlParams.get('from');
                    if (from == null || from == '' || from == undefined) {
                        router.replace({ path: route });
                    } else {
                        router.replace({ path: from.replace('/rp', '') });
                    }
                },
            })
            await data.reload()
        },
        async logout() {
            const data = createResource({
                url: 'logout',
                onSuccess: () => {
                    this.user = getSessionUser();
                    router.push({ name: 'AgencyLogin' })
                },
            })
            await data.reload()
        }
    },
})
