import frappe
from frappe.model.document import Document

class AgreementTemplate(Document):

	def validate(self):
		if self.is_default:
			frappe.db.sql("""
				UPDATE `tabAgreement Template`
				SET is_default = 0
				WHERE organization = %s AND name != %s
			""", (self.organization, self.name))

