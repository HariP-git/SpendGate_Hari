import frappe
from frappe.model.document import Document


class Department(Document):
    def autoname(self):
        self.name = self.department_name