# Copyright (c) 2026, Sophicore and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestOrganizationContacts(IntegrationTestCase):
	"""
	Integration tests for OrganizationContacts.
	Use this class for testing interactions between multiple components.
	"""


	def test_sign_agreement(self):
		
		# Create Org and Contact
		org = frappe.get_doc({
			"doctype": "Organization",
			"organization_name": "Test Agency",
			"organization_type": "Agency",
            "email": "agency@example.com",
            "phone": "9999999999"
		}).insert()

		partner = frappe.get_doc({
			"doctype": "Organization",
			"organization_name": "Test Partner",
			"organization_type": "Referral Partner",
			"agency": org.name,
            "email": "partner@example.com",
            "phone": "8888888888"
		}).insert()

		contact = frappe.get_doc({
			"doctype": "Organization Contacts",
			"organization": org.name,
			"referral_partner": partner.name,
			"firstname": "John",
			"lastname": "Doe",
			"email": "john@example.com",
			"is_required_signed": 1
		}).insert()

		# Test Sign
		# minimalistic base64 gif
		signature_data = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
		
		contact.sign_agreement(
			details={"phone": "1234567890"},
			signature_data=signature_data
		)

		contact.reload()
		self.assertEqual(contact.signed, 1)
		self.assertEqual(contact.phone, "1234567890")
		self.assertTrue(contact.signature_image)
		self.assertTrue("signature" in contact.signature_image)

