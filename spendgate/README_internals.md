B2c — Dangerous Patterns:
Should have identified that the first bug is a recursion pitfall, and the second bug is a race condition. The corrected version of the code is below:
def validate(self):
    self.total_amount = sum(r.amount for r in self.expense_lines)
    self.db_set("total_amount", self.total_amount)
    budget = frappe.get_doc("Budget", self.budget)
    budget.db_set("total_allocated", budget.total_allocated - self.total_amount)


B2d — The Race Condition Question
Yes, both submissions could succeed even though they exceed the budget because of a race condition. When both employees submit their Expense Claims simultaneously, they may both read the same initial value of spent_so_far before either transaction commits. As a result, each controller calculates that there is still enough budget available and allows the submission to proceed. This can lead to a situation where the combined total of the Expense Claims exceeds the budget limit. Frappe/MariaDB does not inherently protect against this specific race condition in this scenario, as it relies on the application logic to enforce constraints. To prevent this, one could implement database-level locking or use transactions with appropriate isolation levels to ensure that only one submission can update the spent_so_far value at a time.


C3 — Expense Line Item Department Update:
Yes, the department on linked Budgets and Expense Claims will update automatically because the Department field is a Link field in both Budgets and Expense Claims. When a Link field is used, it references the name of the linked document. If the name of the linked document (in this case, the Department) is changed, all references to that document will reflect the new name automatically.


D2 — Row-Level Filtering & Data Leaks:
frappe.get_list() is used to fetch data from database which includes the filters and permission access so it will not return that user has no access data and fields.
frappe.get_all() is used to fetch data from the database but it bypass the permissions and filters and return the whole data where the user not had access also.
So frappe.get_all() method exposed to low-privilege then the frappe.get_list() method.


E1 - on_update() — the recursion pitfall:
self.save() is used to save the document and it will call the on_update() method again and it will create a recursion pitfall. So we can use self.db_set() instead of self.save() to avoid the recursion pitfall.


E3 — One Performance Judgment Call:
frappe.get_doc() and frappe.db.get_value()
frappe.get_doc() is used to fetch the whole document from the database and it will return the whole document with all fields and values. It is a heavy operation and it will take more time to fetch the data from the database.
frappe.db.get_value() is used to fetch the specific field value from the database and it will return the specific field value. It is a light operation and it will take less time to fetch the data from the database. So we can use frappe.db.get_value() instead of frappe.get_doc.


H1 — Expense Claim Form Script:
frappe.call is an asynchronous function and it will not wait for the response from the server. So if we use frappe.call inside the validate client event then it will not wait for the response and it will return undefined. So we can use frappe.call inside the onload/refresh client event to wait for the response from the server.


I1 — Query Report: Pending Approvals:
The f-string version of the query report is as follows:
```python
query = f"""
    SELECT
        ec.name AS expense_claim,
        ec.employee AS employee,
        ec.total_amount AS total_amount,
        ec.status AS status,
        ec.creation AS creation_date
    FROM
        `tabExpense Claim` ec
    WHERE
        ec.status = 'Pending'
        AND ec.creation >= '{start_date}'
        AND ec.creation <= '{end_date}'
"""
The parameterized version of the query report is as follows:
```python
query = """
    SELECT
        ec.name AS expense_claim,
        ec.employee AS employee,
        ec.total_amount AS total_amount,
        ec.status AS status,
        ec.creation AS creation_date
    FROM
        `tabExpense Claim` ec
    WHERE
        ec.status = 'Pending'
        AND ec.creation >= %s
        AND ec.creation <= %s
"""
The parameterized version is always preferred because it helps prevent SQL injection attacks by separating the query structure from the data being passed into it. By using placeholders (%s) for the parameters, the database engine can safely handle the input values without executing them as part of the SQL command, thus enhancing security and ensuring that user input does not compromise the integrity of the database.


J1 — Expense Claim Voucher:

When you put a frappe.get_all() call directly inside the Jinja template, it will execute the database query every time the template is rendered. This can lead to multiple database hits, especially if the template is rendered multiple times or if there are many records to fetch. This can significantly slow down the rendering process and increase the load on the database.

The next hand pre-computing the data in the before_print() method allows you to fetch all the necessary data in a single database query before the template is rendered. You can then store this data in a field (e.g., doc.precomputed_field) and reference it in the Jinja template. This approach reduces the number of database queries, improves performance, and ensures that the data is consistent throughout the rendering process.


K2 — Spot the N+1:

Perform 2 operation sepeately and then combine the results to avoid the N+1 query problem. Here's the corrected version of the code:
claims = frappe.get_all("Expense Claim", fields=["name","department"])
department_names = {d.name: d for d in frappe.get_all("Department", fields=["name", "department_name", "department_head"])}
for c in claims:
    dept = department_names.get(c.department)
    if dept:
        print(dept.department_name, dept.department_head) 

for each claim, we first fetch all the departments in a single query and store them in a dictionary for quick lookup. Then, we iterate over the claims and retrieve the corresponding department information from the pre-fetched dictionary. This way, we avoid making a separate database query for each claim, thus preventing the N+1 query problem and improving performance.


N1 — ignore_permissions Audit & JS-Hiding Pitfal

I have used the ignore_permission in the tasks file, audit file and install files which bypass the permission checks the data when the user does not have access the data. So it will also cause the ssecurity issues and data leaks.

Hiding js file is not a security measure because the user can still access the data by using the API or by inspecting the network requests. So it will not prevent the user from accessing the data.








