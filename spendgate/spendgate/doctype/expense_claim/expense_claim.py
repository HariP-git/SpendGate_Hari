# Copyright (c) 2026, Hari and contributors
# For license information, please see license.txt

from erpnext.accounts.doctype import budget
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

		frappe.enqueue("spendgate.notifications.notify_finance_of_new_claim", claim_name=self.name)
		frappe.enqueue("spendgate.api.send_webhook", claim_name=self.name)

	def on_cancel(self):
		if self.status == "Reimbursed":
			frappe.throw("Cannot cancel reimbursed.")
		self.status = "Cancelled"

	def on_trash(self):
		if self.status not in ("Cancelled", "Draft"):
			frappe.throw("Cannot delete an Expense Claim that is not in 'Cancelled' or 'Draft' status.")

	def before_print(self,print_settings=None):
		self.print_summary = f"{self.employee} - {self.department} - {self.expense_date}"


@frappe.whitelist()
def get_remaining_budget(budget):
	budget_amount = frappe.db.get_value(
		"Budget",
		budget,
		"total_allocated"
	)

	if not budget_amount:
		return 0

	spent = frappe.db.sql("""
		SELECT COALESCE(SUM(total_amount), 0)
		FROM `tabExpense Claim`
		WHERE budget = %s
		AND docstatus = 1
	""", budget)[0][0]

	return budget_amount - spent


@frappe.whitelist()
def approve_expense_claim(claim_name):
	claim = frappe.get_doc(
		"Expense Claim",
		claim_name
	)

	if not (
		frappe.has_role("SG Department Head")
		or frappe.has_role("SG Finance Manager")
	):
		frappe.throw(
			"You do not have permission to approve this claim."
		)

	if claim.status != "Pending Approval":
		frappe.throw(
			"Only pending claims can be approved."
		)

	claim.db_set(
		"status",
		"Approved"
	)

	return True


@frappe.whitelist()
def reject_expense_claim(
	claim_name,
	rejection_reason
):
	claim = frappe.get_doc(
		"Expense Claim",
		claim_name
	)

	if not (
		frappe.has_role("SG Department Head")
		or frappe.has_role("SG Finance Manager")
	):
		frappe.throw(
			"You do not have permission to reject this claim."
		)

	if not rejection_reason:
		frappe.throw(
			"Rejection reason is required."
		)

	claim.db_set(
		"status",
		"Rejected"
	)

	claim.db_set(
		"rejection_reason",
		rejection_reason
	)

	return True


@frappe.whitelist()
def reassign_department(
	claim_name,
	department
):
	claim = frappe.get_doc(
		"Expense Claim",
		claim_name
	)

	if not frappe.has_role(
		"SG Finance Manager"
	):
		frappe.throw(
			"Only Finance Manager can reassign departments."
		)

	if not frappe.db.exists(
		"Department",
		department
	):
		frappe.throw(
			"Invalid department."
		)

	claim.db_set(
		"department",
		department
	)

	return True



	