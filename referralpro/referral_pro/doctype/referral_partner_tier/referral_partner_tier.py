import frappe
from frappe.model.document import Document
from frappe import _

class ReferralPartnerTier(Document):
	def validate(self):
		if self.is_default:
			# Check if another default tier exists for the same organization
			existing_default = frappe.db.exists(
				"Referral Partner Tier",
				{
					"organization": self.organization,
					"is_default": 1,
					"name": ["!=", self.name]
				}
			)
			if existing_default:
				frappe.throw(_("Another tier is already set as default for this organization."))
