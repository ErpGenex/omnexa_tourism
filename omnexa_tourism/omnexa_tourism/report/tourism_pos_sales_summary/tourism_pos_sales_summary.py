import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	from_date = getdate(filters.get("from_date") or nowdate())
	to_date = getdate(filters.get("to_date") or nowdate())
	params = {"company": filters.company, "from_date": from_date, "to_date": to_date}
	conditions = ["company = %(company)s", "docstatus < 2", "charge_date BETWEEN %(from_date)s AND %(to_date)s"]
	if filters.get("branch"):
		params["branch"] = filters.branch
		conditions.append("branch = %(branch)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			branch,
			charge_type,
			COUNT(name) AS entries,
			SUM(amount) AS total_amount
		FROM `tabTourism Charge Entry`
		WHERE {' AND '.join(conditions)}
		GROUP BY branch, charge_type
		ORDER BY branch, charge_type
		""",
		params,
		as_dict=True,
	)

	columns = [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 170},
		{"label": _("Charge Type"), "fieldname": "charge_type", "fieldtype": "Data", "width": 140},
		{"label": _("Entries"), "fieldname": "entries", "fieldtype": "Int", "width": 100},
		{"label": _("Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 130},
	]
	return columns, rows
