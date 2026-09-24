import frappe
from frappe.utils import get_url


def after_install():
    default_departments = [
        "Marketing",
        "Travel & Client Entertainment",
        "Equipment & Software",
        "Training"
    ]

    for dept in default_departments:
        if not frappe.db.exists("Department", {"department_name": dept}):
            frappe.get_doc({
                "doctype": "Department",
                "department_name": dept
            }).insert(ignore_permissions=True)

    default_categories = [
        "Travel",
        "Software & Equipment",
        "Client Entertainment",
        "Training"
    ]

    for category in default_categories:
        if not frappe.db.exists(
            "Expense Category",
            {"category_name": category}
        ):
            frappe.get_doc({
                "doctype": "Expense Category",
                "category_name": category
            }).insert(ignore_permissions=True)

    if not frappe.db.exists("SpendGate Settings"):
        frappe.get_doc({
            "doctype": "SpendGate Settings"
        }).insert(ignore_permissions=True)

    settings_url = get_url("/app/spendgate-settings")

    frappe.msgprint(
        f"SpendGate installation completed successfully! "
        f"You can configure settings <a href='{settings_url}'>here</a>."
    )