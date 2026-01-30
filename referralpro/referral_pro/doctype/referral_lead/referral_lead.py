import frappe
from frappe.model.document import Document

class ReferralLead(Document):
	def on_update(self):
		if self.status:
			# Import here to avoid circular dependencies if any
			from referralpro.services.commission import process_lead_commission
			process_lead_commission(self)

