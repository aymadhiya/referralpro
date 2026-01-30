import frappe
from frappe import _
import json

def get_current_org():
    user = frappe.session.user
    if user == "Guest":
        return None
    
    # Cache org lookup in request if possible, but simple db call is fast enough for now
    org_name = frappe.db.get_value("Organization", {"email": frappe.get_value("User", user, "email")}, "name")
    return org_name

@frappe.whitelist()
def get_list(doctype, fields=None, filters=None, order_by=None, page_length=20):
    org_name = get_current_org()
    if not org_name:
        return []

    if isinstance(fields, str):
        fields = json.loads(fields)
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    if not filters:
        filters = {}
    
    # Special handling for Organization doctype
    if doctype == "Organization":
        # Return itself OR its managed partners
        if not filters:
            filters = {}
        filters["or_filters"] = [
            ["name", "=", org_name],
            ["agency", "=", org_name]
        ]
    elif doctype == "Organization Setting":
        filters["organization"] = org_name
    else:
        # Force organization filter for other doctypes
        if not frappe.get_meta(doctype).has_field("organization"):
             # Use a safer check or return empty if doctype doesn't belong to org
             # But for now assuming all agency-managed docs have organization field
             pass
        filters["organization"] = org_name
    
    or_filters = filters.pop("or_filters", None) if filters else None
    return frappe.get_all(doctype, fields=fields, filters=filters, or_filters=or_filters, order_by=order_by, limit_page_length=page_length)

@frappe.whitelist()
def get_doc(doctype, name):
    org_name = get_current_org()
    if not org_name:
        frappe.throw(_("Organization not found"))
    
    if not frappe.db.exists(doctype, name):
         frappe.throw(_("{0} not found").format(doctype))

    # Verify ownership
    if doctype == "Organization":
        if name != org_name:
            frappe.throw(_("Not authorized to view this document"))
    else:
        doc_org = frappe.db.get_value(doctype, name, "organization")
        if doc_org != org_name:
            frappe.throw(_("Not authorized to view this document"))
        
    return frappe.get_doc(doctype, name)

@frappe.whitelist()
def save_doc(doctype, doc):
    org_name = get_current_org()
    if not org_name:
        frappe.throw(_("Organization not found"))

    if isinstance(doc, str):
        doc = json.loads(doc)
    
    if doc.get("name"):
        # Update
        existing_doc = frappe.get_doc(doctype, doc.get("name"))
        
        # Verify ownership
        if doctype == "Organization":
            if existing_doc.name != org_name:
                frappe.throw(_("Not authorized to edit this document"))
        else:
            if existing_doc.get("organization") and existing_doc.organization != org_name:
                 frappe.throw(_("Not authorized to edit this document"))
        
        existing_doc.update(doc)
        existing_doc.flags.ignore_permissions = True
        existing_doc.save()
        return existing_doc
    else:
        # Insert
        if doctype == "Organization":
             # Only allow if it's a Referral Partner being created by an Agency
             if doc.get("organization_type") == "Referral Partner":
                 pass
             else:
                 frappe.throw(_("Cannot create new Organization via this API"))
        
        new_doc = frappe.new_doc(doctype)
        new_doc.update(doc)
        
        # Link to current organization
        if doctype == "Organization":
            new_doc.agency = org_name
        elif doctype == "Referral Partner Invitation":
            new_doc.organization = org_name
            # Set flag for validation to know the context without db lookup
            frappe.flags.agency_org = org_name
        elif doctype == "Organization Setting":
            new_doc.organization = org_name
        else:
            new_doc.organization = org_name
            
        new_doc.flags.ignore_permissions = True
        new_doc.insert()
        return new_doc

@frappe.whitelist()
def delete_doc(doctype, name):
    org_name = get_current_org()
    if not org_name:
        frappe.throw(_("Organization not found"))

    if not frappe.db.exists(doctype, name):
        return True # Already deleted

    # Verify ownership
    if doctype == "Organization":
        org_data = frappe.db.get_value("Organization", name, ["organization_type", "agency"], as_dict=True)
        if not org_data or org_data.organization_type != "Referral Partner" or org_data.agency != org_name:
             frappe.throw(_("Not authorized to delete this organization"))
    elif doctype == "Referral Partner Invitation":
        doc_org = frappe.db.get_value(doctype, name, "organization")
        if doc_org != org_name:
            frappe.throw(_("Not authorized to delete this document"))
    else:
        doc_org = frappe.db.get_value(doctype, name, "organization")
        if doc_org != org_name:
            frappe.throw(_("Not authorized to delete this document"))
    
    frappe.delete_doc(doctype, name, ignore_permissions=True)
    return True
