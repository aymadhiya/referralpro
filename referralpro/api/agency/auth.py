import frappe
from frappe import _

@frappe.whitelist(allow_guest=True, methods=["POST"])
def signup(email: str, full_name: str, mobile_no: str, organization: str):
	"""
	Signup for Agency.
	Creates a User and an Organization linked to that user.
	"""
	from frappe.utils import validate_email_address, validate_phone_number
	
	validate_email_address(email, throw=True)
	validate_phone_number(mobile_no, throw=True)

	if frappe.db.exists("User", email):
		frappe.throw(_("User with this email already exists"))

	if frappe.db.exists("Organization", {"organization_name": organization}):
		frappe.throw(_("Organization with this name already exists"))

	first_name, last_name = full_name, ""
	if " " in full_name:
		first_name, last_name = full_name.split(" ", 1)

	try:
		# Create Organization
		# User creation is now handled in Organization's controller
		org = frappe.new_doc("Organization")
		org.organization_name = organization
		org.type = "Company"
		org.email = email
		org.phone = mobile_no
		org.organization_type = 'Agency'
		
		# Pass user details for after_insert creation
		org.first_name = first_name
		org.last_name = last_name
		
		org.flags.ignore_permissions = True
		org.insert()

		# Send welcome email for password setting
		org.reload()
		if org.user:
			# Auto login
			frappe.local.login_manager.login_as(org.user)

		return {
			"message": "Signup Successful. Please check your email to set your password.",
			"redirect_to": "/agency/dashboard"
		}

	except Exception as e:
		frappe.log_error("Agency Signup Error")
		frappe.throw(_("There was an error during signup: {0}").format(str(e)))
