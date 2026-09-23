import frappe


def log_change(doc, method):
    from frappe.utils import now

    if doc.doctype == "Audit Log" or not frappe.db.exists("DocType", "Audit Log"):
        return

    audit_log = frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doc.doctype,
        "document_name": doc.name,
        "action": method,
        "user": frappe.session.user,
        "timestamp": now()
    })
    audit_log.insert(ignore_permissions=True)