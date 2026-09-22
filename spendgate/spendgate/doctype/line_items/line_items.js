// Copyright (c) 2026, Hari and contributors
// For license information, please see license.txt

frappe.ui.form.on("Line Items", {
    validate(frm) {
        let total_amount = 0;
        frappe.db.get_value("Expense Line", { parent: frm.doc.name }).then(r => {
            r.message.forEach(line => {
                if (line.amount <= 0) {
                    frappe.throw("Expense line amount must be greater than 0");
                }
                total_amount += line.amount;
            });
            frappe.db.set_value("Totals and Status", frm.doc.name, "total_amount", total_amount);
        });
    }
});
