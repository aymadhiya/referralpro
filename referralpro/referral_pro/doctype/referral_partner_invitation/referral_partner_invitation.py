import frappe
from frappe.model.document import Document
from frappe.utils import add_days, now_datetime, get_url
import secrets

class ReferralPartnerInvitation(Document):
    def validate(self):
        # 1. Check for duplicate pending invitations
        if self.is_new():
            duplicate = frappe.db.exists("Referral Partner Invitation", {
                "email": self.email,
                "status": "Pending",
                "organization": self.organization or frappe.flags.agency_org # Use flag if set by API
            })
            if duplicate:
                frappe.throw(frappe._("A pending invitation already exists for this email."))

        # 2. Check if organization already exists
        if not self.referral_partner:
            existing_org = frappe.db.get_value("Organization", {"email": self.email, "organization_type": "Referral Partner"}, "name")
            if existing_org:
                self.referral_partner = existing_org

    def before_insert(self):
        self.token = secrets.token_urlsafe(32)
        self.status = "Pending"
        self.expires_on = add_days(now_datetime(), 7)
        self.invited_by = frappe.session.user
        
        # The field is now named 'organization'
        pass

    def after_insert(self):
        self.create_linked_organization()
        self.send_invitation_email()

    def create_linked_organization(self):
        if self.referral_partner:
            return

        # Check if organization with this email already exists
        existing_org = frappe.db.exists("Organization", {"email": self.email, "organization_type": "Referral Partner"})
        if existing_org:
            self.db_set("referral_partner", existing_org)
            return

        org = frappe.new_doc("Organization")
        org.organization_name = self.organization_name
        org.partner_name = self.partner_name
        org.email = self.email
        org.organization_type = "Referral Partner"
        org.onboarding_status = "Invited"
        org.agency = self.organization
        org.flags.ignore_permissions = True
        org.insert()
        
        self.db_set("referral_partner", org.name)

    def send_invitation_email(self):
        # Generate signup link
        signup_url = f"{get_url()}/partner/signup?token={self.token}"
        
        # Fetch template from Organization Setting
        template_name = frappe.db.get_value("Organization Setting", self.organization, "invitation_email_template")
        
        if template_name:
            template = frappe.get_doc("Email Template", template_name)
            # Render template with context
            context = {
                "partner_name": self.partner_name,
                "organization_name": self.organization_name,
                "agency_name": self.organization,
                "signup_url": signup_url,
                "expires_on": self.expires_on
            }
            subject = frappe.render_template(template.subject, context)
            message = frappe.render_template(template.response, context)
        else:
            # Fallback to default
            subject = f"Invitation to join {self.organization_name} as a Referral Partner"
            message = f"""
            <h3>Hello {self.partner_name},</h3>
            <p>You have been invited to join <b>{self.organization}</b> as a Referral Partner for <b>{self.organization_name}</b>.</p>
            <p>Click the link below to accept the invitation and set up your account:</p>
            <p><a href="{signup_url}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Accept Invitation</a></p>
            <p>Or copy this link: {signup_url}</p>
            <p>This invitation will expire on {self.expires_on}.</p>
            """
        
        frappe.sendmail(
            recipients=[self.email],
            subject=subject,
            message=message,
            reference_doctype=self.doctype,
            reference_name=self.name
        )
