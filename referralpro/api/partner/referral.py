import frappe
from frappe import _

@frappe.whitelist()
def get_lead_form_fields(agency_name):
    """
    Returns custom fields for the specified agency.
    """
    if not agency_name:
        frappe.throw(_("Agency name is required"))
        
    custom_fields = frappe.get_all(
        "Referral Custom Field",
        filters={"organization": agency_name},
        fields=["fieldname", "label", "fieldtype", "options", "is_required", "sequence"],
        order_by="sequence asc"
    )
    
    return custom_fields

@frappe.whitelist()
def submit_referral(agency_name, lead_data, custom_values=None):
    """
    Submits a new referral lead.
    """
    import json
    
    if frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"), frappe.PermissionError)
        
    if isinstance(lead_data, str):
        lead_data = json.loads(lead_data)
        
    if custom_values and isinstance(custom_values, str):
        custom_values = json.loads(custom_values)
        
    # Get the Partner Organization linked to the current user
    partner_org = frappe.db.get_value(
        "Organization", 
        {"user": frappe.session.user, "organization_type": "Referral Partner"}, 
        "name"
    )
    
    if not partner_org:
        frappe.throw(_("Partner Organization not found for current user"))
        
    # Create Lead
    lead = frappe.new_doc("Referral Lead")
    lead.first_name = lead_data.get("first_name")
    lead.last_name = lead_data.get("last_name")
    lead.email = lead_data.get("email")
    lead.phone = lead_data.get("phone")
    lead.deal_value = lead_data.get("deal_value")
    lead.notes = lead_data.get("notes")
    lead.organization = agency_name
    lead.partner = frappe.session.user
    
    # Set default status
    default_status = frappe.db.get_value(
        "Lead Status", 
        {"organization": agency_name}, 
        "name", 
        order_by="sequence asc"
    )
    if default_status:
        lead.status = default_status
        
    # Add Custom Values
    if custom_values:
        for fieldname, value in custom_values.items():
            custom_field_name = frappe.db.get_value(
                "Referral Custom Field", 
                {"organization": agency_name, "fieldname": fieldname}, 
                "name"
            )
            if custom_field_name:
                lead.append("custom_values", {
                    "custom_field": custom_field_name,
                    "value": str(value) if value is not None else ""
                })
                
    lead.insert(ignore_permissions=True)
    
    return {
        "name": lead.name,
        "message": _("Referral submitted successfully")
    }

@frappe.whitelist()
def get_my_referrals(agency_name=None):
    """
    Returns the list of referrals submitted by the current partner.
    """
    if frappe.session.user == "Guest":
        return []
        
    filters = {"partner": frappe.session.user}
    if agency_name:
        filters["organization"] = agency_name
        
    leads = frappe.get_all(
        "Referral Lead",
        filters=filters,
        fields=[
            "name", "first_name", "last_name", "email", "phone", 
            "deal_value", "status", "organization", "creation", "modified"
        ],
        order_by="creation desc"
    )
    
    # Add status info (label, color)
    for lead in leads:
        status_info = frappe.db.get_value(
            "Lead Status", 
            {"organization": lead.organization, "name": lead.status}, 
            ["label", "color"], 
            as_dict=True
        )
        if status_info:
            lead.status_label = status_info.label
            lead.status_color = status_info.color
            
        lead.agency_name = frappe.db.get_value("Organization", lead.organization, "organization_name")
        
    return leads

@frappe.whitelist()
def get_lead_details(name):
    """
    Returns full details of a specific referral lead.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"), frappe.PermissionError)
        
    lead = frappe.get_doc("Referral Lead", name)
    
    # Security: Ensure current user is the partner who submitted the lead
    if lead.partner != frappe.session.user:
        frappe.throw(_("You do not have permission to view this lead"), frappe.PermissionError)
        
    lead_dict = lead.as_dict()
    
    # Add status info
    status_info = frappe.db.get_value(
        "Lead Status", 
        {"organization": lead.organization, "name": lead.status}, 
        ["label", "color"], 
        as_dict=True
    )
    if status_info:
        lead_dict.status_label = status_info.label
        lead_dict.status_color = status_info.color
        
    lead_dict.agency_name = frappe.db.get_value("Organization", lead.organization, "organization_name")
    
    # Add custom values with labels
    custom_values = []
    for row in lead.custom_values:
        custom_field = frappe.get_doc("Referral Custom Field", row.custom_field)
        custom_values.append({
            "fieldname": custom_field.fieldname,
            "label": custom_field.label,
            "value": row.value
        })
    
    lead_dict.custom_values = custom_values
    
    return lead_dict

@frappe.whitelist()
def get_my_transactions():
    """
    Returns the list of commission transactions for the current partner.
    """
    if frappe.session.user == "Guest":
        return []
        
    transactions = frappe.get_all(
        "Referral Transaction",
        filters={"partner": frappe.session.user},
        fields=["name", "date", "referral_lead", "amount", "status", "note", "organization", "commission_rule"],
        order_by="date desc, creation desc"
    )
    
    # Enrich with lead name
    for t in transactions:
        lead = frappe.db.get_value("Referral Lead", t.referral_lead, ["first_name", "last_name"], as_dict=True)
        if lead:
            t.lead_name = f"{lead.first_name} {lead.last_name}"
            
        if t.commission_rule:
             rule = frappe.db.get_value("Commission Rule", t.commission_rule, ["tier", "commission_type", "value"], as_dict=True)
             if rule:
                 # format: Tier Name (10%) or Tier Name ($500)
                 if rule.commission_type == "Percentage":
                     t.commission_rule_title = f"{rule.tier} ({rule.value}%)"
                 else:
                     t.commission_rule_title = f"{rule.tier} (${rule.value})"
             else:
                 t.commission_rule_title = t.commission_rule
            
    return transactions
