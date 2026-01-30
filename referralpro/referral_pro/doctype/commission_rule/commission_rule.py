import frappe
from frappe.model.document import Document
from frappe import _

class CommissionRule(Document):
	def validate(self):
		# Ensure unique rule for Organization + Tier + Lead Status
		existing_rule = frappe.db.exists(
			"Commission Rule",
			{
				"organization": self.organization,
				"tier": self.tier,
				"lead_status": self.lead_status,
				"name": ["!=", self.name]
			}
		)
		if existing_rule:
			frappe.throw(_("A commission rule already exists for this Tier and Lead Status."))
