import frappe


frappe.whitelist(allow_guest=True)
def get_expense_claims_safe():
    user = frappe.session.user
    user_roles = frappe.get_roles(user)

    if "SG Staff" in user_roles:
        claims = frappe.get_list(
            "Expense Claim",
            filters={"employee": user},
            fields=["name", "employee", "department", "total_amount", "status", "expense_date"]
        )
    elif "SG Department Head" in user_roles:
        department = frappe.get_value("Employee", {"user_id": user}, "department")
        claims = frappe.get_list(
            "Expense Claim",
            filters={"department": department},
            fields=["name", "employee", "department", "total_amount", "status", "expense_date"]
        )
    else:
        claims = []

    return claims

frappe.whitelist(allow_guest=True)
def get_expense_claims_unsafe():
    claims = frappe.get_all(
        "Expense Claim",
        fields=["*"]
    )
    return claims

