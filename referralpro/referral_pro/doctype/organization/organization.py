import frappe
from frappe import _
from frappe.model.document import Document

class Organization(Document):
	def validate(self):
		if frappe.db.exists("Organization", {"organization_name": self.organization_name, "name": ["!=", self.name]}):
			frappe.throw(_("Organization Name must be unique"))

	def after_insert(self):
		self.create_user()
		self.create_default_team()

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
			if frappe.db.exists("Role", "Agency Owner"):
				user_doc.append("roles", {"role": "Agency Owner"})
			
			user_doc.flags.ignore_permissions = True
			user_doc.insert()
			user = user_doc.name
		else:
			# User exists, check if role is present
			user_doc = frappe.get_doc("User", user)
			existing_roles = [r.role for r in user_doc.roles]
			if "Agency Owner" not in existing_roles and frappe.db.exists("Role", "Agency Owner"):
				user_doc.append("roles", {"role": "Agency Owner"})
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
