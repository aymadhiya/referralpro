import frappe
from frappe.model.document import Document

class OrganizationSetting(Document):
	def autoname(self):
		self.name = self.organization
