import frappe
from frappe.utils import today


def check_budget_thresholds():
    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "budget_threshold_check",
            "date": today(),
        },
        "name",
    )

    if last_run:
        return

    settings = frappe.get_doc(
        "SpendGate Settings",
        "SpendGate Settings",
    )

    threshold = settings.low_budget_alert_threshold_percent

    budgets = frappe.get_all(
        "Budget",
        filters={"status": "Active"},
        fields=["name", "department", "total_allocated"],
    )

    for budget in budgets:
        spent = frappe.db.sql(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM `tabExpense Claim`
            WHERE budget = %s
            AND docstatus = 1
            """,
            budget.name,
        )[0][0]

        utilization_percent = (
            spent / budget.total_allocated * 100
            if budget.total_allocated
            else 0
        )

        if utilization_percent > threshold:
            department_head_email = frappe.db.get_value(
                "Department",
                budget.department,
                "department_head_email",
            )

            if department_head_email:
                frappe.sendmail(
                    recipients=department_head_email,
                    subject=f"Budget Alert: {budget.name}",
                    message=(
                        f"The budget for {budget.name} has exceeded "
                        f"the low budget alert threshold of {threshold}%. "
                        f"Current utilization is "
                        f"{utilization_percent:.2f}%."
                    ),
                )

            frappe.get_doc(
                {
                    "doctype": "Notification Log",
                    "for_user": "Administrator",
                    "type": "Alert",
                    "subject": f"Budget Alert: {budget.name}",
                    "email_content": (
                        f"The budget for {budget.name} has exceeded "
                        f"the low budget alert threshold of {threshold}%. "
                        f"Current utilization is "
                        f"{utilization_percent:.2f}%."
                    ),
                }
            ).insert(ignore_permissions=True)

    frappe.get_doc(
        {
            "doctype": "Audit Log",
            "action": "budget_threshold_check",
            "date": today(),
        }
    ).insert(ignore_permissions=True)

    frappe.db.commit()