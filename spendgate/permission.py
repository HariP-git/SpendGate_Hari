import frappe

def expense_claim_query(user):
    if "SG Finance Manager" in frappe.get_roles(user):
        return ""

    if "SG Department Head" in frappe.get_roles(user):
        department = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            "department"
        )

        if department:
            return f"`tabExpense Claim`.`department` = {frappe.db.escape(department)}"

        return "1=0"

    if "SG Staff" in frappe.get_roles(user):
        return f"`tabExpense Claim`.`employee` = {frappe.db.escape(user)}"
    