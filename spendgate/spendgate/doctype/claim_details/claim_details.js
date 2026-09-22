// Copyright (c) 2026, Hari and contributors
// For license information, please see license.txt
frappe.ui.form.on("Claim Details", {
    onload(frm) {
        if (frm.is_new() && !frm.doc.expense_date) {
            frm.set_value("expense_date", frappe.datetime.get_today());
        }
    },
    validate(frm) {
        if (frm.doc.budget) {
            frappe.db.get_value("Budget", frm.doc.budget, "department")
                .then(r => {
                    if (r.message.department !== frm.doc.department) {
                        frappe.throw("The department on the Expense Claim must match the department on the linked Budget");
                    }
                });
        }
    }



});



