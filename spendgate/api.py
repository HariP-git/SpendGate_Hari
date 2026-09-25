import frappe

@frappe.whitelist(allow_guest=True)
def share_expense_claim(claim_name, user_email):
    frappe.share.add(
        "Expense Claim",
        claim_name,
        user_email,
        read=1
    )

    return {
        "success": True
    }


@frappe.whitelist()
def get_expense_claims():
    return frappe.get_list(
        "Expense Claim",
        fields=[
            "name",
            "employee",
            "department",
            "total_claimed_amount"
        ]
    )


@frappe.whitelist()
def get_expense_claims_unsafe():
    return frappe.get_all(
        "Expense Claim",
        fields=[
            "name",
            "employee",
            "department",
            "total_claimed_amount"
        ]
    )


@frappe.whitelist()
def get_budget_status():
    budget_name = frappe.form_dict.get("budget_name")

    if not budget_name:
        frappe.local.response.http_status_code = 404
        return {"error": "Not found"}

    budget = frappe.db.get_value(
        "Budget",
        budget_name,
        ["total_allocated"],
        as_dict=True
    )

    if not budget:
        frappe.local.response.http_status_code = 404
        return {"error": "Not found"}

    spent = frappe.db.sql(
        """
        SELECT COALESCE(SUM(el.amount), 0)
        FROM `tabExpense Claim` ec
        INNER JOIN `tabExpense Line` el
            ON el.parent = ec.name
        WHERE ec.budget = %s
        AND ec.docstatus = 1
        """,
        budget_name
    )[0][0]

    allocated = budget.total_allocated or 0
    spent = spent or 0
    remaining = allocated - spent

    utilization_percent = (
        (spent / allocated) * 100
        if allocated
        else 0
    )

    return {
        "allocated": allocated,
        "spent": spent,
        "remaining": remaining,
        "utilization_percent": utilization_percent
    }
    
    
def send_webhook(claim_name):
    import requests
    settings = frappe.get_single("SpendGate Settings")
    if not settings.web_hook_url:
        return
    doc = frappe.get_doc("Expense Claim", claim_name)
    payload = {"event": "claim_submitted", "claim": doc.name, "amount": doc.total_amount}
    try:
        r = requests.post(settings.web_hook_url, json=payload, timeout=5)
        r.raise_for_status()
        frappe.log_error(f"Webhook sent successfully for claim {claim_name}", "Webhook Info")
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Webhook failed: {e}", "Webhook Error")
    except Exception as e:
        frappe.log_error(f"Webhook failed: {e}", "Webhook Error")