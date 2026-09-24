import frappe
from hypothesis import settings

def notify_finance_of_new_claim(claim_name):
    claim = frappe.get_doc("Expense Claim", claim_name)

    settings = frappe.get_single("SpendGate Settings")
    email = settings.finance_email

    if not email:
        return

    frappe.sendmail(
        recipients=email,
        subject=f"New Expense Claim: {claim_name}",
        message=f"""
Employee: {claim.employee}
Department: {claim.department}
Amount: {claim.total_amount}
Date: {claim.expense_date}""")