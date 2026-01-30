import frappe
from frappe import _

@frappe.whitelist()
def get_partner_organizations():
    """
    Returns a list of organizations (Agencies) that the current user is a partner for.
    It checks the 'Organization' doctype where 'organization_type' is 'Referral Partner'
    and the 'user' field matches the current user. Then it fetches the 'agency' linked to that organization.
    """
    if frappe.session.user == "Guest":
        return []

    # Get the Partner Organizations linked to the current user
    partner_orgs = frappe.get_all(
        "Organization",
        filters={
            "user": frappe.session.user,
            "organization_type": "Referral Partner"
        },
        fields=["name", "organization_name", "agency"]
    )

    if not partner_orgs:
        return []

    agency_list = []
    seen_agencies = set()

    for org in partner_orgs:
        if org.agency and org.agency not in seen_agencies:
            # Fetch Agency Details
            agency_details = frappe.db.get_value(
                "Organization", 
                org.agency, 
                ["name", "organization_name", "logo"], 
                as_dict=True
            )
            if agency_details:
                agency_list.append(agency_details)
                seen_agencies.add(org.agency)

    return agency_list

@frappe.whitelist()
def get_organization_contacts():
    """
    Returns list of contacts for the current partner organization.
    """
    if frappe.session.user == "Guest":
        return []

    partner_org = frappe.db.get_value("Organization", {"user": frappe.session.user, "organization_type": "Referral Partner"}, "name")
    if not partner_org:
        return []
        
    contacts = frappe.get_all("Organization Contacts", 
        filters={"referral_partner": partner_org},
        fields=["name", "firstname", "lastname", "email", "phone", "is_primary", "status", "signed"]
    )
    return contacts

@frappe.whitelist()
def save_organization_contacts(contacts):
    """
    Saves a list of organization contacts (Directors) for the logged-in partner organization.
    Checks if Agreement is required by the Agency and sets up contacts accordingly.
    """
    from frappe.utils import now_datetime
    import json
    
    if frappe.session.user == "Guest":
         frappe.throw(_("Not logged in"), frappe.PermissionError)

    # 1. Get Current Partner Organization
    partner_org = frappe.db.get_value("Organization", {"user": frappe.session.user, "organization_type": "Referral Partner"}, ["name", "agency", "phone"], as_dict=True)
    if not partner_org:
        frappe.throw(_("Partner Organization not found"))

    # 2. Check Agreement Requirement from Agency
    agreement_required = False
    org_settings = frappe.db.get_value("Organization Setting", {"organization": partner_org.agency}, ["agreement_required"], as_dict=True)
    if org_settings and org_settings.agreement_required:
        agreement_required = True

    agreement_template = None
    if agreement_required:
        agreement_template = frappe.db.get_value("Agreement Template", {"organization": partner_org.agency, "is_default": 1}, "name")

    # 3. Process Contacts
    if isinstance(contacts, str):
        contacts = json.loads(contacts)

    saved_contacts = []
    
    for contact_data in contacts:
        # Validate data
        if not contact_data.get("email") or not contact_data.get("name"):
            continue

        email = contact_data.get("email")
        
        # Check if exists
        existing_contact_name = frappe.db.get_value("Organization Contacts", 
            {"referral_partner": partner_org.name, "email": email}, 
            "name"
        )
        
        if existing_contact_name:
            contact = frappe.get_doc("Organization Contacts", existing_contact_name)
            is_new = False
        else:
            contact = frappe.new_doc("Organization Contacts")
            is_new = True

        contact.organization = partner_org.agency
        contact.referral_partner = partner_org.name
        
        full_name = contact_data.get("name", "")
        firstname, lastname = full_name, ""
        if " " in full_name:
            # Simple split, frontend sends structured but we reconstruct 'name' in frontend before sending. 
            # Wait, frontend sends firstname/lastname AND name? 
            # My previous plan said frontend sends "name" constructed. 
            # Actually I should rely on structured data if available.
            # Let's support both. Use firstname/lastname if in data, else split name.
            pass

        if contact_data.get("firstname"):
             firstname = contact_data.get("firstname")
             lastname = contact_data.get("lastname") or ""
        elif " " in full_name:
             firstname, lastname = full_name.split(" ", 1)
        
        contact.firstname = firstname
        contact.lastname = lastname
        
        contact.email = email
        contact.phone = contact_data.get("phone") or partner_org.phone
        contact.is_primary = contact_data.get("is_primary", 0)
        
        if agreement_required:
            contact.status = "Agreement Pending"
            contact.agreement_template = agreement_template
            contact.agreement_recevied_date = now_datetime()
            contact.is_required_signed = 1
        else:
            contact.status = "Active"
            contact.is_required_signed = 0

        contact.flags.ignore_permissions = True
        contact.save(ignore_permissions=True)
        saved_contacts.append(contact.name)

        if agreement_required and is_new:
            # Send Email only on creation (or if explicitly requested via another API)
            contact.send_agreement_email()

    # Update Organization Onboarding Status
    # Check if ALL have signed if Upsert happened?
    # Or just set to Pending if ANY require signature and not signed?
    # Simple logic: If agreement required, set Pending. 
    # But wait, if they are ALREADY signed, sending "Pending" might revert status?
    # Check if all signed.
    if agreement_required:
        # Check total signed vs total required
        # If we just saved/updated, we might have new contacts requiring signature
        total_required = frappe.db.count("Organization Contacts", {"referral_partner": partner_org.name, "is_required_signed": 1})
        total_signed = frappe.db.count("Organization Contacts", {"referral_partner": partner_org.name, "is_required_signed": 1, "signed": 1})
        
        if total_required > 0 and total_signed >= total_required:
             new_status = "Completed"
        else:
             new_status = "Pending Agreement"
             
        frappe.db.set_value("Organization", partner_org.name, "onboarding_status", new_status)
    else:
        frappe.db.set_value("Organization", partner_org.name, "onboarding_status", "Completed")
        # Ensure no contacts are blocking
        frappe.db.set_value("Organization Contacts", {"referral_partner": partner_org.name}, "is_required_signed", 0)

    return {
        "message": _("Contacts saved successfully"),
        "contacts": saved_contacts
    }

@frappe.whitelist()
def get_my_profile():
    """
    Returns the profile details of the current partner organization.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"), frappe.PermissionError)

    partner_org = frappe.db.get_value(
        "Organization", 
        {"user": frappe.session.user, "organization_type": "Referral Partner"}, 
        ["name", "organization_name", "email", "phone", "address", "city", "state", "country", "postal_code", "tax_id"], 
        as_dict=True
    )
    
    if not partner_org:
        return {}
        
    return partner_org

@frappe.whitelist()
def update_my_profile(data):
    """
    Updates the profile details of the current partner organization.
    """
    import json
    
    if frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"), frappe.PermissionError)
        
    if isinstance(data, str):
        data = json.loads(data)
        
    partner_org_name = frappe.db.get_value(
        "Organization", 
        {"user": frappe.session.user, "organization_type": "Referral Partner"}, 
        "name"
    )
    
    if not partner_org_name:
        frappe.throw(_("Partner Organization not found"))
        
    org = frappe.get_doc("Organization", partner_org_name)
    
    # Update allowed fields
    allowed_fields = ["organization_name", "phone", "address", "city", "state", "country", "postal_code", "tax_id"]
    for field in allowed_fields:
        if field in data:
            setattr(org, field, data[field])
            
    org.save(ignore_permissions=True)
    
    return {
        "message": _("Profile updated successfully"),
        "profile": get_my_profile()
    }
