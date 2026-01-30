frappe.ui.form.on('Organization', {
    refresh: function (frm) {
        if (frm.doc.organization_type === 'Referral Partner' && frm.doc.onboarding_status !== 'Completed') {
            frm.add_custom_button(__('Send Agreement Emails'), function () {
                frm.call({
                    method: 'send_agreement_emails',
                    doc: frm.doc,
                    callback: function (r) {
                        // Optional: refresh?
                    }
                });
            });
        }
    }
});
