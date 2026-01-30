# Copyright (c) 2026, ReferralPro and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CommissionRuleThreshold(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		commission_type: DF.Literal["Percentage", "Fixed Amount"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		threshold_from: DF.Float
		threshold_to: DF.Float
		value: DF.Float
	# end: auto-generated types

	pass
