# Copyright (c) 2024, Referral Pro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import base64
from frappe.utils.file_manager import save_file

class OrganizationContacts(Document):
	def before_insert(self):
		self.set_agreement_requirements()

	def set_agreement_requirements(self):
		if not self.organization:
			return

		# Check if Agency requires agreement
		org_settings = frappe.db.get_value("Organization Setting", 
			{"organization": self.organization}, 
			["agreement_required"], 
			as_dict=True
		)

		if org_settings and org_settings.agreement_required:
			self.is_required_signed = 1
			
			if not self.status:
				self.status = "Agreement Pending"
			
			if not self.agreement_recevied_date:
				self.agreement_recevied_date = now_datetime()

			# Set Default Agreement Template if not set
			if not self.agreement_template:
				# 1. Try to get from Referral Partner Organization
				partner_template = frappe.db.get_value("Organization", self.referral_partner, "agreement_template")
				if partner_template:
					self.agreement_template = partner_template
				else:
					# 2. Fallback to Agency Default
					default_template = frappe.db.get_value("Agreement Template", 
						{"organization": self.organization, "is_default": 1}, 
						"name"
					)
					if default_template:
						self.agreement_template = default_template

	def on_update(self):
		self.check_organization_completion()

	def check_organization_completion(self):
		"""
		Checks if all required contacts for the Partner Organization have signed.
		If so, updates the Organization's onboarding_status to 'Completed'.
		"""
		if not self.referral_partner:
			return

		# Only check if agreement is required for this org type setup
		# Verify Organization Status is not already completed? 
		current_status = frappe.db.get_value("Organization", self.referral_partner, "onboarding_status")
		if current_status == "Completed":
			return

		# Count totals
		total_required = frappe.db.count("Organization Contacts", {"referral_partner": self.referral_partner, "is_required_signed": 1})
		total_signed = frappe.db.count("Organization Contacts", {"referral_partner": self.referral_partner, "is_required_signed": 1, "signed": 1})

		if total_required > 0 and total_signed >= total_required:
			frappe.db.set_value("Organization", self.referral_partner, "onboarding_status", "Completed")

	@frappe.whitelist()
	def send_agreement_email(self):
		"""
		Sends an email to the director with a link to sign the agreement.
		"""
		if not self.email or not self.is_required_signed:
			return

		try:
			base_url = frappe.utils.get_url()
			signing_link = f"{base_url}/partner/sign-agreement/{self.name}"
			
			agency_name = frappe.db.get_value('Organization', self.organization, 'organization_name')
			subject = f"Action Required: Sign Agreement for {agency_name}"
			
			recipient_name = f"{self.firstname} {self.lastname or ''}"

			message = f"""
			<p>Dear {recipient_name},</p>
			
			<p>You have been added as a director for your organization's partnership account.</p>
			
			<p>Please click the link below to review and sign the required agreement:</p>
			
			<p><a href="{signing_link}" style="background-color: #059669; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Sign Agreement</a></p>
			
			<p>If the button above does not work, please copy and paste the following link into your browser:</p>
			<p>{signing_link}</p>
			
			<p>Thank you.</p>
			"""

			frappe.sendmail(
				recipients=[self.email],
				subject=subject,
				message=message,
				now=True
			)
			# Log email sent?
		except Exception as e:
			frappe.log_error(f"Failed to send agreement email to {self.email}: {str(e)}", "Agreement Email Error")
			frappe.throw(f"Failed to send email: {str(e)}")

	@frappe.whitelist()
	def sign_agreement(self, details=None, signature_data=None):
		"""
		Handles the signing process including saving the signature image
		and updating contact details.
		"""
		if self.signed:
			return {"message": "Already Signed"}

		if details:
			if isinstance(details, str):
				import json
				details = json.loads(details)
			
			self.firstname = details.get("firstname", self.firstname)
			self.lastname = details.get("lastname", self.lastname)
			self.phone = details.get("phone", self.phone)
			self.email = details.get("email", self.email)
			
			if details.get("signature_image"): # If uploading file directly through other means
				pass # Handled separately usually, but here we expect base64 `signature_data`

		if signature_data:
			# Decode base64
			try:
				if "base64," in signature_data:
					signature_data = signature_data.split("base64,")[1]
				
				file_content = base64.b64decode(signature_data)
				filename = f"signature_{self.name}.png"
				
				# Create File
				saved_file = save_file(
					fname=filename,
					content=file_content,
					dt="Organization Contacts",
					dn=self.name,
					is_private=0
				)
				self.signature_image = saved_file.file_url

			except Exception as e:
				frappe.log_error(f"Failed to save signature for {self.name}: {str(e)}")
				# Continue signing process even if image fails? Or throw?
				# Let's throw for now as it is "Signature Required"
				frappe.throw(f"Failed to save signature: {str(e)}")

		self.process_signature()
		return {"message": "Agreement Signed Successfully"}

	@frappe.whitelist()
	def process_signature(self):
		"""
		Marks the contact as signed.
		"""
		if self.signed:
			return
		
		self.signed = 1
		self.signed_date = now_datetime()
		self.status = "Active"
		self.signer_name = f"{self.firstname} {self.lastname or ''}"
		self.signer_email = self.email
		self.save(ignore_permissions=True) # This will trigger on_update -> check_organization_completion
