import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.AuthenticationError:
        return {
            "success_key": False,
            "message": "Invalid login credentials"
        }
    
    user = frappe.get_doc("User", frappe.session.user)
    return {
        "success_key": True,
        "message": "Logged In",
        "default_route": "/agency/dashboard", # Logic to determine route can be added here
        "full_name": user.full_name
    }

@frappe.whitelist()
def validate_user_roles():
    # Example logic
    user = frappe.session.user
    roles = frappe.get_roles(user)
    return roles

@frappe.whitelist()
def get_user_info():
    user = frappe.get_doc("User", frappe.session.user)
    
    is_agency_user = False
    is_partner_user = False
    
    # Check if Agency
    if frappe.db.exists("Organization", {"user": user.name, "organization_type": "Agency"}):
         is_agency_user = True
         
    # Check if Partner
    partner_org = frappe.db.get_value("Organization", {"user": user.name, "organization_type": "Referral Partner"}, ["name", "onboarding_status"], as_dict=True)
    onboarding_status = "Completed"
    
    if partner_org:
        is_partner_user = True
        onboarding_status = partner_org.onboarding_status
            
    return {
        "user": user.name,
        "email": user.email,
        "full_name": user.full_name,
        "roles": frappe.get_roles(user.name),
        "is_agency_user": is_agency_user,
        "is_partner_user": is_partner_user,
        "onboarding_status": onboarding_status
    }
