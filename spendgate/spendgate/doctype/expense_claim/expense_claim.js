frappe.ui.form.on("Expense Claim", {
    setup(frm) {
        frm.set_query("budget", () => {
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

        frm.trigger("loadBudget");
    },

    refresh(frm) {
        frm.dashboard.clear_headline();

        if (frm.doc.status === "Pending") {
            frm.dashboard.add_indicator(
                ("Pending Approval"),
                "orange"
            );

            if (
                frappe.user.has_role("SG Department Head") ||
                frappe.user.has_role("SG Finance Manager")
            ) {
                frm.add_custom_button(("Approve"), () => {
                    frappe.call({
                        method: "spendgate.spendgate.doctype.expense_claim.expense_claim.approve_expense_claim",
                        args: {
                            claim_name: frm.doc.name
                        },
                        callback(r) {
                            if (!r.exc) {
                                frm.reload_doc();
                            }
                        }
                    });
                });

                frm.add_custom_button(("Reject Claim"), () => {
                    frappe.prompt(
                        {
                            label: ("Rejection Reason"),
                            fieldname: "rejection_reason",
                            fieldtype: "Small Text",
                            reqd: 1
                        },
                        values => {
                            frappe.confirm(
                                ("Reject this Expense Claim?"),
                                () => {
                                    frappe.call({
                                        method: "spendgate.spendgate.doctype.expense_claim.expense_claim.reject_expense_claim",
                                        args: {
                                            claim_name: frm.doc.name,
                                            rejection_reason: values.rejection_reason
                                        },
                                        callback(r) {
                                            if (!r.exc) {
                                                frm.reload_doc();
                                            }
                                        }
                                    });
                                }
                            );
                        },
                        ("Reject Expense Claim"),
                        ("Reject")
                    );
                });
            }
        }

        if (frm.doc.status === "Approved") {
            frm.dashboard.add_indicator(("Approved"), "green");
        }

        if (frm.doc.status === "Rejected") {
            frm.dashboard.add_indicator(("Rejected"), "red");
        }

        frm.add_custom_button(("Reassign Department"), () => {
            frappe.prompt(
                {
                    label: ("Department"),
                    fieldname: "department",
                    fieldtype: "Link",
                    options: "Department",
                    reqd: 1
                },
                values => {
                    frappe.confirm(
                        ("Reassign this claim to {0}?", [values.department]),
                        () => {
                            frappe.call({
                                method: "spendgate.spendgate.doctype.expense_claim.expense_claim.reassign_department",
                                args: {
                                    claim_name: frm.doc.name,
                                    department: values.department
                                },
                                callback(r) {
                                    if (!r.exc) {
                                        frm.set_value("department", values.department);
                                        frm.trigger("department");
                                    }
                                }
                            });
                        }
                    );
                },
                ("Reassign Department"),
                ("Continue")
            );
        });
    },

    department(frm) {
        frm.trigger("loadBudget");
    },

    budget(frm) {
        frm.trigger("loadBudget");
    },

    loadBudget(frm) {
        if (!frm.doc.budget) {
            frm.budgetRemaining = 0;
            return;
        }

        frappe.call({
            method: "spendgate.spendgate.doctype.expense_claim.expense_claim.get_remaining_budget",
            args: {
                budget: frm.doc.budget
            },
            callback(r) {
                if (!r.exc) {
                    frm.budgetRemaining = r.message || 0;

                    frm.dashboard.add_indicator(
                        ("Budget Remaining: {0}", [
                            frm.budgetRemaining
                        ]),
                        "blue"
                    );
                }
            }
        });
    },

    expenseLinesAmount(frm) {
        const total = (frm.doc.expense_line || []).reduce(
            (sum, row) => sum + (row.amount || 0),
            0
        );

        frm.set_value("total_amount", total);

        if (
            frm.budgetRemaining !== undefined &&
            total > frm.budgetRemaining
        ) {
            frappe.msgprint(
                ("Warning: Total amount exceeds the remaining budget of {0}.", [
                    frm.budgetRemaining
                ])
            );
        }
    }
});