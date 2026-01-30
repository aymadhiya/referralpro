// Copyright (c) 2024, Referral Pro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Organization Contacts', {
    refresh: function (frm) {

    },
    organization: function (frm) {
        if (frm.doc.organization) {
            // Optional: Fetch default template immediately on client side for better UX
            // But backend logic handles it securely.
        }
    }
});
