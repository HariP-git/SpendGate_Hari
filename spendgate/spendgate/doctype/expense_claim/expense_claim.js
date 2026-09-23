// Copyright (c) 2026, Hari and contributors
// For license information, please see license.txtd

frappe.ui.form.on("Expense Claim", {
    setup(frm) {
        frm.set_query("budget", function () {
            return {
                filters: {
                    department: frm.doc.department,
                    fiscal_year: frappe.defaults.get_default("fiscal_year")
                }
            };
        });
        
    },
    onload(frm) {
        if (frm.is_new() && !frm.doc.expense_date) {
            frm.set_value("expense_date", frappe.datetime.get_today());
        }
    },
    refresh(frm) {
        frm.dashboard.clear_headline();
        if (frm.doc.status === "Pending Approval") {
            frm.dashboard.add_indicator(__("Pending Approval"), "orange");
            if (frappe.user.has_role(["Department Head", "Finance Manager"])) {
                frm.add_custom_button(__('Approve'), function () {
                    frappe.call({
                        method: "spendgate.spendgate.doctype.expense_claim.expense_claim.approve_expense_claim",
                        args: { expense_claim: frm.doc.name },
                        callback: function (r) {
                            if (!r.exc) {
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }
        } else if (frm.doc.status === "Approved") {
            frm.dashboard.add_indicator(__("Approved"), "green");
        } else if (frm.doc.status === "Rejected") {
            frm.dashboard.add_indicator(__("Rejected"), "red");
        }

    },
    expense_lines_amount(frm, cdt, cdn) {
        const expense_line = frappe.get_doc(cdt, cdn);
        const total_amount = frm.doc.expense_lines.reduce((sum, line) => sum + (line.amount || 0), 0);
        frm.set_value("total_amount", total_amount);

        if (frm.doc.budget) {
            frappe.call({
                method: "spendgate.spendgate.doctype.expense_claim.expense_claim.get_remaining_budget",
                args: { budget: frm.doc.budget },
                callback: function (r) {
                    if (!r.exc) {
                        const remaining_budget = r.message;
                        if (total_amount > remaining_budget) {
                            frappe.msgprint(__("Warning: Total amount exceeds the remaining budget of {0}.", [remaining_budget]));
                        }
                    }
                }
            });
        }
    },

});
    
let d = new frappe.ui.Dialog({
    title: __("Reject Expense Claim"),
    fields: [
        {
            label: __("Rejection Reason"),
            fieldname: "rejection_reason",
            fieldtype: "Small Text",
            reqd: 1
        }
    ],
    primary_action_label: __("Reject"),
    primary_action(values) {
        frappe.call({
            method: "spendgate.spendgate.doctype.expense_claim.expense_claim.reject_expense_claim",
            args: {
                expense_claim: frm.doc.name,
                rejection_reason: values.rejection_reason
            },
            callback: function (r) {
                if (!r.exc) {
                    frm.reload_doc();
                    d.hide();
                }
            }
        });
    }
}); 

d.show();