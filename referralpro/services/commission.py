import frappe
from frappe import _
from frappe.utils import flt, nowdate, get_first_day, get_last_day, add_months

def process_lead_commission(lead_doc):
    """
    Evaluates if a commission should be paid for the lead and creates a transaction.
    Triggered on Referral Lead status change.
    """
    # 1. Check if Organization has Referral Partner feature enabled (implicit via rule existence)
    
    # 2. Get Partner Tier
    # We need to find the specific tier for this partner in this organization
    # Assuming 'Organization Team Member' or 'Referral Partner Invitation' links User to Org with Tier
    # For now, let's fetch the tier from the Partner organization record if strictly B2B, 
    # but more likely we need a direct link between User and Tier for this Agency.
    # Let's check 'Referral Partner Tier' based on a lookup or default.
    
    # Finding the tier:
    # A partner (User) belongs to a Partner Organization.
    # That Partner Organization has a 'tier' field relative to the Agency (Organization).
    # Wait, the current schema links User -> Organization (as Partner). 
    # Let's look up the Partner Organization record managed by this Agency.
    
    partner_org_name = frappe.db.get_value("Organization", {"user": lead_doc.partner, "organization_type": "Referral Partner"}, "name")
    if not partner_org_name:
        # Fallback: Maybe simple user partner? 
        return
        
    # We need to find the relationship between this Partner Org and the Agency to get the Tier.
    # In this app, it seems 'Organization' doc itself creates the relationship via 'agency' field.
    partner_org_doc = frappe.get_doc("Organization", partner_org_name)
    
    # If this partner is not managed by the lead's agency, skip (shouldn't happen with proper data)
    if partner_org_doc.agency != lead_doc.organization:
        return

    # 3. Find Matching Rule
    # Rule must match: Organization (Agency), Tier, and New Lead Status
    tier = partner_org_doc.tier if hasattr(partner_org_doc, 'tier') else None # Use standard fieldname
    # Let's check if 'tier' field exists on Organization, otherwise use Default Tier logic
    
    if not tier:
        # Find default tier for this agency
        tier = frappe.db.get_value("Referral Partner Tier", {"organization": lead_doc.organization, "is_default": 1}, "name")
        
    if not tier:
        return # No tier configuration found
        
    rule = frappe.db.get_value("Commission Rule", {
        "organization": lead_doc.organization, 
        "tier": tier, 
        "lead_status": lead_doc.status
    }, ["name", "calculation_metric", "calculation_period", "commission_type", "value", "is_tiered"], as_dict=True)
    
    if not rule:
        return # No rule defined for this status
        
    # 4. Check if transaction already exists for this Rule + Lead
    exists = frappe.db.exists("Referral Transaction", {
        "referral_lead": lead_doc.name,
        "commission_rule": rule.name
    })
    if exists:
        return # Already processed
        
    # 5. Calculate Amount
    amount = 0.0
    
    if not rule.is_tiered:
        # Simple Calculation
        if rule.commission_type == "Fixed Amount":
            amount = flt(rule.value)
        else:
            # Percentage - based on Deal Value
            deal_value = flt(lead_doc.deal_value) if hasattr(lead_doc, 'deal_value') else 0.0
            amount = (deal_value * flt(rule.value)) / 100.0
    else:
        # Tiered Calculation
        amount = calculate_tiered_commission(rule, lead_doc.organization, lead_doc.partner, lead_doc)

    if amount > 0:
        create_transaction(lead_doc, rule.name, amount)

def calculate_tiered_commission(rule, agency, partner, lead_doc=None):
    """
    Calculates commission amount based on tiered thresholds.
    """
    # 1. Determine Period Date Range
    start_date, end_date = get_period_dates(rule.calculation_period)
    
    # 2. Calculate Metric Value (Total prior leads/value in this period)
    metric_value = 0.0
    
    filters = {
        "organization": agency,
        "partner": partner,
        "creation": ["between", [start_date, end_date]]
    }
    
    if rule.calculation_metric == "Lead Count":
        # Count all leads by this partner in this period
        metric_value = frappe.db.count("Referral Lead", filters)
    elif rule.calculation_metric == "Total Deal Value":
        # Sum deal values
        result = frappe.db.get_value("Referral Lead", filters, "sum(deal_value)")
        metric_value = flt(result) if result else 0.0
        
    # 3. Find applicable threshold
    # We need the full doc to access child table
    rule_doc = frappe.get_doc("Commission Rule", rule.name)
    
    applied_rate = 0.0
    rate_type = "Fixed Amount"
    match_found = False
    
    # Sort thresholds to find where metric_value fits
    for threshold in rule_doc.thresholds:
        # Strict checking: value must be within range [from, to] (inclusive)
        # If threshold_to is 0, it means 'and onwards'
        if threshold.threshold_from <= metric_value and (threshold.threshold_to >= metric_value or threshold.threshold_to == 0):
             applied_rate = threshold.value
             rate_type = threshold.commission_type
             match_found = True
             break
             
    if not match_found:
        return 0.0

    # 4. Calculate Final Amount
    if rate_type == "Fixed Amount":
        return flt(applied_rate)
    else:
        # Percentage
        deal_value = flt(lead_doc.deal_value) if lead_doc and hasattr(lead_doc, 'deal_value') else 0.0
        return (deal_value * flt(applied_rate)) / 100.0

def get_period_dates(period):
    today = nowdate()
    if period == "Monthly":
        return get_first_day(today), get_last_day(today)
    elif period == "Yearly":
        # Simplified yearly logic
        return f"{today[:4]}-01-01", f"{today[:4]}-12-31"
    # ... Add other periods as needed
    return "2000-01-01", "2099-12-31" # Lifetime

def create_transaction(lead_doc, rule_name, amount):
    doc = frappe.new_doc("Referral Transaction")
    doc.organization = lead_doc.organization
    doc.partner = lead_doc.partner
    doc.referral_lead = lead_doc.name
    doc.commission_rule = rule_name
    doc.amount = amount
    doc.status = "Pending"
    doc.date = nowdate()
    doc.note = _("Auto-generated based on rule: {0}").format(rule_name)
    doc.insert(ignore_permissions=True)
