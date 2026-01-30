import frappe
from frappe import _
from frappe.utils import add_months, get_first_day, get_last_day, nowdate, flt, getdate

@frappe.whitelist()
def get_dashboard_stats():
    """
    Returns aggregated stats for the Agency Dashboard.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Not logged in"), frappe.PermissionError)

    # Get Agency Organization linked to current user
    agency_name = frappe.db.get_value("Organization", {"user": frappe.session.user, "organization_type": "Agency"}, "name")
    
    if not agency_name:
        # Fallback or empty if not agency
        return {}
        
    stats = {
        "total_referrals": 0,
        "referral_growth": 0,
        "active_partners": 0,
        "partners_growth": 0,
        "total_commission_paid": 0.0,
        "pending_agreements": 0,
        "lead_chart": {"labels": [], "data": []},
        "financial_chart": {"labels": [], "data": []},
        "recent_transactions": [],
        "avg_commission": 0.0,
        "conversion_rate": 0.0
    }
    
    # 1. Total Referrals & Growth
    stats["total_referrals"] = frappe.db.count("Referral Lead", {"organization": agency_name})
    
    # Growth (vs last month)
    last_month_start = get_first_day(add_months(nowdate(), -1))
    last_month_end = get_last_day(add_months(nowdate(), -1))
    this_month_start = get_first_day(nowdate())
    
    leads_last_month = frappe.db.count("Referral Lead", {
        "organization": agency_name,
        "creation": ["between", [last_month_start, last_month_end]]
    })
    leads_this_month = frappe.db.count("Referral Lead", {
        "organization": agency_name,
        "creation": [">=", this_month_start]
    })
    
    if leads_last_month > 0:
        stats["referral_growth"] = flt(((leads_this_month - leads_last_month) / leads_last_month) * 100, 1)
    else:
        stats["referral_growth"] = 100 if leads_this_month > 0 else 0

    # 2. Active Partners & Growth
    stats["active_partners"] = frappe.db.count("Organization", {"agency": agency_name, "organization_type": "Referral Partner", "status": "Active"})
    
    # New partners this month (Growth proxy)
    new_partners_month = frappe.db.count("Organization", {
        "agency": agency_name, 
        "organization_type": "Referral Partner",
        "creation": [">=", this_month_start]
    })
    stats["partners_growth"] = new_partners_month

    # 3. Commissions Paid
    paid_commissions = frappe.db.sql("""
        SELECT SUM(amount) FROM `tabReferral Transaction`
        WHERE organization = %s AND status = 'Paid'
    """, (agency_name,))
    stats["total_commission_paid"] = flt(paid_commissions[0][0]) if paid_commissions else 0.0

    # 4. Pending Agreements
    stats["pending_agreements"] = frappe.db.count("Organization", {
        "agency": agency_name, 
        "organization_type": "Referral Partner", 
        "onboarding_status": "Pending Agreement"
    })
    
    # 5. Charts (Last 6 Months)
    months = []
    lead_counts = []
    comm_amounts = []
    
    for i in range(5, -1, -1):
        month_date = add_months(nowdate(), -i)
        start = get_first_day(month_date)
        end = get_last_day(month_date)
        label = getdate(start).strftime("%b")
        months.append(label)
        
        # Lead Count
        count = frappe.db.count("Referral Lead", {
            "organization": agency_name,
            "creation": ["between", [start, end]]
        })
        lead_counts.append(count)
        
        # Commission Amount (Approved + Paid usually reflects performance)
        comm = frappe.db.sql("""
            SELECT SUM(amount) FROM `tabReferral Transaction`
            WHERE organization = %s AND creation BETWEEN %s AND %s AND status != 'Rejected'
        """, (agency_name, start, end))
        comm_amounts.append(flt(comm[0][0]) if comm else 0.0)
        
    stats["lead_chart"] = {"labels": months, "data": lead_counts}
    stats["financial_chart"] = {"labels": months, "data": comm_amounts}
    
    # 6. Recent Transactions
    stats["recent_transactions"] = frappe.get_all(
        "Referral Transaction",
        filters={"organization": agency_name},
        fields=["name", "date", "partner", "amount", "status"],
        order_by="creation desc",
        limit=5
    )
    
    # 7. Avg Commission & Conversion Rate
    total_tx_count = frappe.db.count("Referral Transaction", {"organization": agency_name, "status": ["!=", "Rejected"]})
    total_comm_value = sum(comm_amounts) # Approx from chart data
    stats["avg_commission"] = flt(total_comm_value / total_tx_count, 2) if total_tx_count > 0 else 0.0
    
    total_leads = stats["total_referrals"]
    # Assuming 'Won' and 'Closed' are success statuses. 
    # Fetching success statuses dynamically would be better but simple logic for now:
    # Get all statuses with is_completed=1? Or just check a few know ones.
    # Let's count leads that have a generated transaction as "converted" effectively.
    converted_leads = frappe.db.count("Referral Transaction", {"organization": agency_name})
    stats["conversion_rate"] = flt((converted_leads / total_leads) * 100, 1) if total_leads > 0 else 0.0
    
    return stats
