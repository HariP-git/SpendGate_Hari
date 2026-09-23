import frappe

def get_claims_pending_approval():
    frappe.qb = frappe.get_query_builder()
    EC = frappe.qb.DocType("Expense Claim")
    result = (
        frappe.qb.from_(EC)
        .select(EC.name, EC.employee, EC.department, EC.total_amount, EC.expense_date)
        .where(EC.status == "Pending Approval")
        .order_by(EC.expense_date.asc())
        .run(as_dict=True)
    )
    return result

def reassign_department_claims(from_dept, to_dept):
    try:
        frappe.db.sql(
            """
            UPDATE `tabExpense Claim`
            SET department = %s
            WHERE department = %s AND status = 'Draft'
            """,
            (to_dept, from_dept),
        )
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error reassigning claims from {from_dept} to {to_dept}: {str(e)}")
        raise

frappe.whitelist(allow_guest=True)
def share_expense_claim(claim_name, user_email):
    try:
        frappe.share.add(
            doctype="Expense Claim",
            name=claim_name,
            user=user_email,
            read=1,
            write=0,
            share=0
        )
        return {"status": "success", "message": f"Read access granted to {user_email} for claim {claim_name}"}
    except Exception as e:
        frappe.log_error(f"Error sharing claim {claim_name} with {user_email}: {str(e)}")
        return {"status": "error", "message": str(e)}   

