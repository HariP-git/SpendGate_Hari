# Copyright (c) 2026, Hari and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.core.doctype.user.user import now_datetime
from frappe.model.naming import make_autoname


class TotalsandStatus(Document):
	def autoname(self):
			year = now_datetime().strftime("%Y")
			self.name = make_autoname(f"EXP-.{year}-.#####")
