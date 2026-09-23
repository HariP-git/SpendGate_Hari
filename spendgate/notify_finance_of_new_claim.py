import frappe

def notify_finance_of_new_claim(claim_name):
    try:
        claim_doc = frappe.get_doc("Expense Claim", claim_name)
        finance_email = frappe.get_value("Department", claim_doc.department, "finance_email")

        if finance_email:
            subject = f"New Expense Claim Submitted: {claim_name}"
            message = f"""
            A new expense claim has been submitted.

            Claim Name: {claim_name}
            Employee: {claim_doc.employee}
            Department: {claim_doc.department}
            Total Amount: {claim_doc.total_amount}
            Expense Date: {claim_doc.expense_date}

            Please review the claim at your earliest convenience.
            """
            frappe.sendmail(recipients=finance_email, subject=subject, message=message)
        else:
            frappe.log_error(f"No finance email found for department {claim_doc.department}. Cannot notify finance of new claim {claim_name}.")
    except Exception as e:
        frappe.log_error(f"Error notifying finance of new claim {claim_name}: {str(e)}")
