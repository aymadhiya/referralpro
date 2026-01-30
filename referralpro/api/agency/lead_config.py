import frappe
from frappe import _
import json

def get_current_agency_org():
    user = frappe.session.user
    if user == "Guest":
        return None
    
    org_name = frappe.db.get_value("Organization", {"user": user}, "name")
    if not org_name:
        # Fallback to email lookup if user link is missing
        email = frappe.db.get_value("User", user, "email")
        org_name = frappe.db.get_value("Organization", {"email": email}, "name")
        
    return org_name

@frappe.whitelist()
def get_custom_fields():
    """
    Returns custom fields for the current agency.
    """
    org_name = get_current_agency_org()
    if not org_name:
        return []
        
    fields = frappe.get_all(
        "Referral Custom Field",
        filters={"organization": org_name},
        fields=["name", "label", "fieldname", "fieldtype", "options", "is_required", "sequence"],
        order_by="sequence asc"
    )
    
    return fields

@frappe.whitelist()
def save_custom_field(field_data):
    """
    Saves/Updates a custom field.
    """
    if isinstance(field_data, str):
        field_data = json.loads(field_data)
        
    org_name = get_current_agency_org()
    if not org_name:
        frappe.throw(_("Organization not found for user"))
        
    if field_data.get("name"):
        doc = frappe.get_doc("Referral Custom Field", field_data.get("name"))
        if doc.organization != org_name:
             frappe.throw(_("Not authorized to edit this field"))
    else:
        doc = frappe.new_doc("Referral Custom Field")
        doc.organization = org_name
        
    doc.label = field_data.get("label")
    doc.fieldname = field_data.get("fieldname")
    doc.fieldtype = field_data.get("fieldtype")
    doc.options = field_data.get("options")
    doc.is_required = field_data.get("is_required", 0)
    doc.sequence = field_data.get("sequence", 0)
    
    doc.save(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def delete_custom_field(name):
    """
    Deletes a custom field.
    """
    org_name = get_current_agency_org()
    if not org_name:
         frappe.throw(_("Not authorized"))
         
    doc = frappe.get_doc("Referral Custom Field", name)
    if doc.organization != org_name:
        frappe.throw(_("Not authorized to delete this field"))
        
    doc.delete(ignore_permissions=True)
    return True
