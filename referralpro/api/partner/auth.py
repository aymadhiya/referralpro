import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def verify_invitation_token(token: str):
    """
    Verifies the invitation token and returns invitation details.
    """
    if not token:
        frappe.throw(_("Token is missing"))

    invitation = frappe.db.get_value("Referral Partner Invitation", {"token": token}, ["name", "partner_name", "organization_name", "email", "status", "expires_on", "organization"], as_dict=True)
    
    if not invitation:
        return {
            "success_key": False,
            "message": "Invitation token is expired/invalid!"
        }

    if invitation.status != "Pending":
        return {
            "success_key": False,
            "message": "This invitation has already been {0}".format(invitation.status.lower())
        }

    if invitation.expires_on and invitation.expires_on < now_datetime():
        # Update status to Expired if it hasn't been updated yet
        frappe.db.set_value("Referral Partner Invitation", invitation.name, "status", "Expired")
        return {
            "success_key": False,
            "message": "This invitation has expired"
        }

    # Check if user exists and has password
    user_exists = frappe.db.exists("User", invitation.email)
    has_password = False
    if user_exists:
        # Check if password exists in __Auth table
        auth_pass = frappe.db.get_value("__Auth", {"doctype": "User", "name": invitation.email, "fieldname": "password"}, "password", order_by=None)
        if auth_pass:
            has_password = True
    
    invitation.user_exists = user_exists
    invitation.has_password = has_password

    # Fetch inviting organization title
    if invitation.organization:
        invitation.organization_title = frappe.db.get_value("Organization", invitation.organization, "organization_name")

    return {
        "success_key": True,
        "invitation": invitation
    }

@frappe.whitelist(allow_guest=True, methods=["POST"])
def complete_signup(token: str, password: str = None, partner_name: str = None, organization_name: str = None, partner_type: str = "Company"):
    """
    Completes the partner signup by setting password, creating Org, and marking invite as Accepted.
    """
    if not token:
        frappe.throw(_("Token is required"))

    invitation_name = frappe.db.get_value("Referral Partner Invitation", {"token": token, "status": "Pending"}, "name")
    if not invitation_name:
        frappe.throw(_("Invalid or expired invitation"))

    invitation = frappe.get_doc("Referral Partner Invitation", invitation_name)
    
    # Check if password is required
    user_exists = frappe.db.exists("User", invitation.email)
    has_password = False
    if user_exists:
        # Check if password exists in __Auth table
        auth_pass = frappe.db.get_value("__Auth", {"doctype": "User", "name": invitation.email, "fieldname": "password"}, "password", order_by=None)
        if auth_pass:
            has_password = True
    
    if not has_password and not password:
         frappe.throw(_("Password is required"))


    # Update names if provided
    if partner_name:
        invitation.partner_name = partner_name
    if organization_name:
        invitation.organization_name = organization_name

    try:
        # Check Agreement Logic first
        agreement_required = False
        org_settings = frappe.db.get_value("Organization Setting", {"organization": invitation.organization}, ["agreement_required"], as_dict=True)
        if org_settings and org_settings.agreement_required:
            agreement_required = True

        # 0. Create or Update User directly
        user_name = invitation.email
        if frappe.db.exists("User", user_name):
            user = frappe.get_doc("User", user_name)
            if password:
                user.new_password = password
            if "Referral Partner" not in [r.role for r in user.roles]:
                user.append("roles", {"role": "Referral Partner"})
            user.flags.ignore_password_policy = True
            user.save(ignore_permissions=True)
        else:
            user = frappe.new_doc("User")
            user.email = user_name
            user.first_name = partner_name or invitation.partner_name
            user.new_password = password
            user.send_welcome_email = 0
            user.flags.no_welcome_mail = True
            user.append("roles", {"role": "Referral Partner"})
            user.flags.ignore_password_policy = True
            user.insert(ignore_permissions=True)

        # 1. Create or Update Organization (Partner Org)
        org_name = frappe.db.get_value("Organization", {"email": invitation.email, "organization_type": "Referral Partner"}, "name")
        if org_name:
            org = frappe.get_doc("Organization", org_name)
        else:
            org = frappe.new_doc("Organization")
            org.email = invitation.email
            org.organization_type = 'Referral Partner'
        
        org.organization_name = invitation.organization_name
        org.partner_name = invitation.partner_name
        org.type = partner_type
        org.agency = invitation.organization # Link to inviting agency
        
        # Link default agreement template from Agency
        default_template = frappe.db.get_value("Agreement Template", 
            {"organization": invitation.organization, "is_default": 1}, "name")
        if default_template:
            org.agreement_template = default_template

        if partner_type == "Company":
            org.onboarding_status = "Pending Director Setup"
        else:
            # For Individual, check if agreement is required
            if agreement_required:
                org.onboarding_status = "Pending Agreement"
            else:
                org.onboarding_status = "Completed"
        
        org.flags.ignore_permissions = True
        org.save() if org_name else org.insert()

        # 3. Update Invitation
        invitation.status = "Accepted"
        invitation.accepted_on = now_datetime()
        invitation.referral_partner = org.name
        invitation.save(ignore_permissions=True)

        # Handle Agreement Logic
        # agreement_required calculation moved to top

        if agreement_required:
            if partner_type == "Individual":
                # Create Contact for Individual
                # Fetch Default Agreement Template
                agreement_template = frappe.db.get_value("Agreement Template", {"organization": invitation.organization, "is_default": 1}, "name")
                
                contact = frappe.new_doc("Organization Contacts")
                contact.organization = invitation.organization
                contact.referral_partner = org.name
                contact.firstname = user.first_name
                contact.lastname = user.last_name
                contact.email = user.email
                contact.phone = org.phone
                contact.is_primary = 1
                contact.status = "Agreement Pending"
                contact.agreement_template = agreement_template
                contact.agreement_recevied_date = now_datetime()
                contact.is_required_signed = 1
                contact.flags.ignore_permissions = True
                contact.insert()

                # Send Agreement Email to Individual
                contact.send_agreement_email()
            
        if partner_type == "Company":
             # Auto Login and Return response for Director Setup
            frappe.local.login_manager.login_as(user.name)
            return {
                "message": _("Signup successful! Please add director details."),
                "redirect_to": "/partner/setup-directors", # Frontend route for adding directors
                "agreement_required": agreement_required,
                "partner_type": "Company"
            }

        # 4. Auto Login
        frappe.local.login_manager.login_as(user.name)
        if agreement_required:
            if partner_type == "Individual":
                return {
                    "message": _("Signup successful! Please sign the agreement."),
                    "redirect_to": "/partner/verification-pending"
                }
        return {
            "message": _("Signup successful! Welcome to the Partner Portal."),
            "redirect_to": "/partner/dashboard"
        }

    except frappe.exceptions.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), _("Partner Signup Validation Error"))
        # Pass the validation error message directly to the user
        frappe.throw(str(e))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Partner Signup Error"))
        frappe.throw(_("There was an error during signup: {0}").format(str(e)))
