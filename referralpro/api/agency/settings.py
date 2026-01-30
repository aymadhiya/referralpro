import frappe
from frappe import _
import json

@frappe.whitelist()
def get_agency_labels():
    user = frappe.session.user
    if user == "Guest":
        return {}
    
    org_name = frappe.db.get_value("Organization", {"email": frappe.get_value("User", user, "email")}, "name")
    if not org_name:
        return {}

    org = frappe.get_doc("Organization", org_name)
    
    # Reload doc to ensure we get latest schema if it was updated recently (though migration is usually needed)
    # frappe.reload_doc("referralpro", "doctype", "organization") 
    
    labels = org.agency_labels
    if isinstance(labels, str):
        try:
            labels = json.loads(labels)
        except:
            labels = {}
            
    if not labels:
        labels = {
            "status_pending": "Pending",
            "status_in_progress": "In Progress",
            "status_converted": "Converted",
            "status_rejected": "Rejected"
        }
    
    return labels

@frappe.whitelist()
def save_agency_labels(labels):
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Not authorized"))

    org_name = frappe.db.get_value("Organization", {"email": frappe.get_value("User", user, "email")}, "name")
    if not org_name:
        frappe.throw(_("Organization not found for user"))

    if isinstance(labels, str):
        labels = json.loads(labels)

    org = frappe.get_doc("Organization", org_name)
    org.agency_labels = json.dumps(labels)
    org.flags.ignore_permissions = True # Ensure we can save even if permissions are tricky
    org.save()

    return True
