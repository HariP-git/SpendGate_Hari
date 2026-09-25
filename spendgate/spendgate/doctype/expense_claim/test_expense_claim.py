from frappe.tests.utils import FrappeTestCase
import frappe


def create_user():
	email = f"test_{frappe.generate_hash(length=6)}@example.com"

	user = frappe.get_doc({
		"doctype": "User",
		"email": email,
		"first_name": "Test User",
		"enabled": 1,
		"user_type": "System User"
	})
	user.insert()

	return user


def create_department(department_name=None):
	if department_name is None:
		department_name = f"Test Department {frappe.generate_hash(length=6)}"

	department = frappe.get_doc({
		"doctype": "Department",
		"department_name": department_name
	})
	department.insert()

	return department


def create_expense_category(category_name=None):
	if category_name is None:
		category_name = f"Test Category {frappe.generate_hash(length=6)}"

	category = frappe.get_doc({
		"doctype": "Expense Category",
		"category_name": category_name
	})
	category.insert()

	return category


def create_vendor(vendor_name=None):
	if vendor_name is None:
		vendor_name = f"Test Vendor {frappe.generate_hash(length=6)}"

	vendor = frappe.get_doc({
		"doctype": "Vendor",
		"vendor_name": vendor_name
	})
	vendor.insert()

	return vendor


def create_budget(department, total_allocated=1000):
	budget = frappe.get_doc({
		"doctype": "Budget",
		"department": department,
		"fiscal_year": 2026,
		"fiscal_quarter": "Q1",
		"total_allocated": total_allocated
	})
	budget.insert()

	return budget


def create_expense_claim(
	employee=None,
	department=None,
	budget=None,
	description="Test expense claim",
	expense_date=None,
	amount=100,
	status="Draft"
):
	if employee is None:
		employee = create_user().name

	if department is None:
		department = create_department().name

	if budget is None:
		budget = create_budget(department).name

	if expense_date is None:
		expense_date = frappe.utils.today()

	expense_claim = frappe.get_doc({
		"doctype": "Expense Claim",
		"employee": employee,
		"department": department,
		"budget": budget,
		"expense_date": expense_date,
		"description": description,
		"status": status
	})

	expense_claim.append("expense_line", {
		"category": create_expense_category().name,
		"vendor": create_vendor().name,
		"amount": amount
	})

	expense_claim.insert()

	return expense_claim


class TestExpenseClaim(FrappeTestCase):

	def setUp(self):
		pass

	def test_happy_path(self):
		"""Test that a valid Expense Claim saves as a draft without error."""
		department = create_department()
		budget = create_budget(department.name)

		expense_claim = create_expense_claim(
			department=department.name,
			budget=budget.name,
			amount=100
		)

		self.assertEqual(expense_claim.docstatus, 0)   
