import frappe

def create_roles():
    if not frappe.db.exists("Role", "Referral Partner"):
        role = frappe.new_doc("Role")
        role.role_name = "Referral Partner"
        role.desk_access = 0
        role.insert(ignore_permissions=True)
        print("Created Referral Partner Role")
    else:
        print("Referral Partner Role already exists")

if __name__ == "__main__":
    frappe.connect()
    create_roles()
    frappe.db.commit()
