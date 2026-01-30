import frappe
import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def get_signing_info(contact_name):
    """
    Fetches the signing context: All Contacts for the Partner Org, Agency Name, and Rendered Agreement Content.
    """
    if not contact_name:
        frappe.throw(_("Invalid Link"))

    # Fetch "Active" Contact Doc
    try:
        active_contact_doc = frappe.get_doc("Organization Contacts", contact_name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Invalid or Expired Signing Link"))

    # Fetch All Contacts for this Partner Organization
    all_contacts = frappe.get_all("Organization Contacts",
        filters={"referral_partner": active_contact_doc.referral_partner},
        fields=["name", "firstname", "lastname", "email", "phone", "signed", "signed_date", "signature_image", "is_required_signed"]
    )

    # Fetch Partner Organization for context
    partner_org = None
    if active_contact_doc.referral_partner:
        partner_org = frappe.get_doc("Organization", active_contact_doc.referral_partner)

    # Fetch Agency Name
    agency_name = frappe.db.get_value("Organization", active_contact_doc.organization, "organization_name")

    # Fetch and Render Agreement Content
    html_content = ""
    if active_contact_doc.agreement_template:
        html_content = frappe.db.get_value("Agreement Template", active_contact_doc.agreement_template, "html_content")
        
        if not html_content:
             html_content = frappe.db.get_value("Agreement Template", active_contact_doc.agreement_template, "content")

        if html_content:
            # Prepare Render Context
            # We provide fields as top-level variables AND the objects for flexibility
            render_context = active_contact_doc.as_dict()
            render_context["doc"] = active_contact_doc
            
            if partner_org:
                render_context["organization"] = partner_org
                render_context["organization_name"] = partner_org.organization_name
            else:
                render_context["organization"] = {}
                render_context["organization_name"] = ""

            render_context["frappe"] = frappe

            try:
                html_content = frappe.render_template(str(html_content), render_context)
            except Exception as e:
                frappe.log_error(f"Template Rendering Error: {str(e)}", "Agreement Signing")
                # Optionally: return a helpful error in the HTML for debugging if it's a dev site
                # html_content += f"<div style='color:red'>Rendering Error: {str(e)}</div>"

    return {
        "active_contact_id": contact_name,
        "contacts": all_contacts,
        "agency_name": agency_name,
        "html_content": html_content,
        "already_signed": active_contact_doc.signed
    }
    

@frappe.whitelist(allow_guest=True)
def sign_agreement(contact_name, details=None, signature_data=None):
    """
    Marks the contact as signed and checks if the Partner Organization is fully fully signed.
    Accepts optional details and signature_data (base64 image).
    """
    if not contact_name:
        frappe.throw(_("Invalid Request"))

    contact = frappe.get_doc("Organization Contacts", contact_name)
    
    if contact.signed:
         return {"message": "Already Signed"}

    # Use Controller Method
    return contact.sign_agreement(details=details, signature_data=signature_data)


@frappe.whitelist(allow_guest=True)
def delete_ref_data():
    organizations = frappe.get_all("Organization", {"organization_type":"Referral Partner"})
    for org in organizations:
        frappe.db.delete("Referral Partner Invitation", {"referral_partner": org.name})
        frappe.db.delete("Organization Contacts", {"referral_partner": org.name})
        frappe.db.delete("Organization Team", {"organization": org.name})
        frappe.db.delete("User", {"email": org.email})
        frappe.db.delete("Organization", {"name": org.name})
    frappe.db.commit()
