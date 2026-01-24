import frappe

def execute():
	roles = ["Agency Partner", "Agency Owner"]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role,
				"desk_access": 0
			}).insert(ignore_permissions=True)
