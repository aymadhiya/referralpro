import frappe
from frappe import _
from frappe.model.document import Document

class Organization(Document):
	def validate(self):
		if frappe.db.exists("Organization", {"organization_name": self.organization_name, "name": ["!=", self.name]}):
			frappe.throw(_("Organization Name must be unique"))

	def before_insert(self):
		self.set_default_agreement_template()

	def after_insert(self):
		self.create_user()
		self.create_default_team()

	def set_default_agreement_template(self):
		if self.organization_type == "Referral Partner" and self.agency and not self.agreement_template:
			# Fetch default agreement template for the Agency
			default_template = frappe.db.get_value("Agreement Template", 
				{"organization": self.agency, "is_default": 1}, 
				"name"
			)
			if default_template:
				self.agreement_template = default_template

	def create_user(self):
		# Create a new user if it doesn't exist
		if not self.email:
			return
			
		user = frappe.db.get_value("User", {"email": self.email}, "name")
		if not user:
			user_doc = frappe.new_doc("User")
			user_doc.email = self.email
			# Use attributes passed from API or fallbacks
			user_doc.first_name = getattr(self, "first_name", self.organization_name)
			user_doc.last_name = getattr(self, "last_name", "")
			user_doc.new_password = getattr(self, "new_password", None)
			user_doc.mobile_no = self.phone
			user_doc.enabled = 1
			user_doc.send_welcome_email = 0
			user_doc.flags.no_welcome_mail = True
			
			# Check if Agency Owner role exists, otherwise might need another default
			role = "Agency Owner"
			if self.organization_type == "Referral Partner":
				role = "Referral Partner"
			
			if frappe.db.exists("Role", role):
				user_doc.append("roles", {"role": role})
			
			user_doc.flags.ignore_permissions = True
			user_doc.insert()
			user = user_doc.name
		else:
			# User exists, check if role is present
			user_doc = frappe.get_doc("User", user)
			existing_roles = [r.role for r in user_doc.roles]

			role = "Agency Owner"
			if self.organization_type == "Referral Partner":
				role = "Referral Partner"			
			if role not in existing_roles and frappe.db.exists("Role", role):
				user_doc.append("roles", {"role": role})
				user_doc.flags.ignore_permissions = True
				user_doc.save()
			
		# Link user to Organization
		frappe.db.set_value("Organization", self.name, "user", user)
		self.user = user # Update local instance

	def create_default_team(self):
		if not self.user:
			return

		team = frappe.new_doc("Organization Team")
		team.organization = self.name
		team.team_name = "General"
		team.is_default = 1
		team.user = self.user
		
		# Add self as member
		team.append("organization_team_member", {
			"user": self.user,
			"role": "Agency Owner" if frappe.db.exists("Role", "Agency Owner") else None # Use appropriate role for member
		})
		
		team.flags.ignore_permissions = True
		team.insert()

	@frappe.whitelist()
	def send_agreement_emails(self):
		"""
		Sends agreement emails to all directors who haven't signed yet.
		"""
		if self.organization_type != "Referral Partner":
			frappe.throw(_("This action is only available for Referral Partners"))

		contacts = frappe.get_all("Organization Contacts", 
			filters={
				"referral_partner": self.name,
				"is_required_signed": 1,
				"signed": 0
			},
			fields=["name"]
		)

		if not contacts:
			frappe.msgprint(_("No pending agreements found to send."))
			return

		count = 0
		for c in contacts:
			contact_doc = frappe.get_doc("Organization Contacts", c.name)
			try:
				contact_doc.send_agreement_email()
				count += 1
			except Exception:
				pass # Continue to next or log

		frappe.msgprint(_("Agreement emails sent to {0} directors.").format(count))
