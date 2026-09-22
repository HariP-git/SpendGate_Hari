# Copyright (c) 2026, Hari and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.core.doctype.user.user import now_datetime
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Budget(Document):
	def autoname(self):
		year = now_datetime().strftime("%Y")
		self.name = make_autoname(f"BUD-.{year}-.#####")

	def validate(self):
		if self.total_allocated <= 0:
			frappe.throw("Total Allocated must be greater than 0")

		if frappe.db.exists("Budget", {
			"department": self.department,
			"fiscal_year": self.fiscal_year,
			"fiscal_quarter": self.fiscal_quarter
		}):
			frappe.throw("A Budget already exists for the same department, fiscal year, and fiscal quarter")