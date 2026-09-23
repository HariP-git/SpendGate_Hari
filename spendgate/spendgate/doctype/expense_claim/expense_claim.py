# Copyright (c) 2026, Hari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.core.doctype.user.user import now_datetime
from frappe.model.naming import make_autoname


class ExpenseClaim(Document):
	def autoname(self):
			year = now_datetime().strftime("%Y")
			self.name = make_autoname(f"EXP-.{year}-.#####")

	def validate(self):	
		total_amount = 0
		for line in self.expense_line:
			if line.amount <= 0:
				frappe.throw("Each expense line's amount must be greater than 0.")
			total_amount += line.amount
		self.total_amount = total_amount
		if self.department != frappe.db.get_value("Budget", self.budget, "department"):
			frappe.throw("The Expense Claim's department must match the department on the linked Budget.")


	def before_submit(self):
		budget_doc = frappe.get_doc("Budget", self.budget)
		spent_so_far = frappe.db.sql("""
			SELECT COALESCE(SUM(total_amount), 0) FROM `tabExpense Claim`
			WHERE budget = %s AND docstatus = 1 AND name != %s
		""", (self.budget, self.name or ""))[0][0]

		if spent_so_far + self.total_amount > budget_doc.total_allocated:
			overage_amount = (spent_so_far + self.total_amount) - budget_doc.total_allocated
			remaining_budget = budget_doc.total_allocated - spent_so_far
			frappe.throw(f"Submitting this Expense Claim would exceed the allocated budget for department '{self.department}'. Over by: {overage_amount}. Remaining budget: {remaining_budget}.")

	def on_submit(self):
		budget_doc = frappe.get_doc("Budget", self.budget)
		spent_so_far = frappe.db.sql("""
			SELECT COALESCE(SUM(total_amount), 0) FROM `tabExpense Claim`
			WHERE budget = %s AND docstatus = 1 AND name != %s
		""", (self.budget, self.name or ""))[0][0]
		self.remaining_budget_at_submission = budget_doc.total_allocated - spent_so_far - self.total_amount

		if not self.approved_by:
			self.approved_by = frappe.session.user

		frappe.enqueue('spendgate.notify.notify_finance_of_new_claim', claim_name=self.name)

	def on_cancel(self):
		if self.status == "Reimbursed":
			frappe.throw("Cannot cancel an Expense Claim that has already been reimbursed. Please contact finance for a reversal process.")
		self.status = "Cancelled"

	def on_trash(self):
		if self.status not in ("Cancelled", "Draft"):
			frappe.throw("Cannot delete an Expense Claim that is not in 'Cancelled' or 'Draft' status. Please contact finance for assistance.")

	@frappe.whitelist(allow_guest=True)
	def approve_expense_claim(self):
		department_head = frappe.db.get_value("Department", self.department, "department_head")
		finance_manager = frappe.db.get_value("Role", {"name": "SG Finance Manager"}, "name")
		if frappe.session.user not in [department_head, finance_manager]:
			frappe.throw("You do not have permission to approve this Expense Claim.")

		self.status = "Approved"
		self.db_set("status", "Approved", update_modified=False)

	@frappe.whitelist(allow_guest=True)
	def get_remaining_budget(self):
		remaining_budget = frappe.db.sql("""
			SELECT COALESCE(SUM(total_amount), 0) FROM `tabExpense Claim`
			WHERE budget = %s AND docstatus = 1 AND name != %s
		""", (self.budget, self.name or ""))[0][0]
		return remaining_budget	


	@frappe.whitelist(allow_guest=True)
	def reject_expense_claim(self, rejection_reason):
		department_head = frappe.db.get_value("Department", self.department, "department_head")
		finance_manager = frappe.db.get_value("Role", {"name": "SG Finance Manager"}, "name")
		if frappe.session.user not in [department_head, finance_manager]:
			frappe.throw("You do not have permission to reject this Expense Claim.")
		if not rejection_reason:
			frappe.throw("Rejection reason is required.")
		self.status = "Rejected"
		self.rejection_reason = rejection_reason


