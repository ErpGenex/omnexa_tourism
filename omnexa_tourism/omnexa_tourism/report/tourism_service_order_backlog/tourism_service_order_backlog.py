import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	target_date = getdate(filters.get("date") or nowdate())
	params = {"company": filters.company, "target_date": target_date}
	conditions = ["company = %(company)s", "docstatus < 2"]
	if filters.get("branch"):
		params["branch"] = filters.branch
		conditions.append("branch = %(branch)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			branch,
			service_category,
			status,
			COUNT(name) AS order_count,
			SUM(CASE WHEN status IN ('Ordered', 'In Progress') AND service_date < %(target_date)s THEN 1 ELSE 0 END) AS overdue_count
		FROM `tabTourism Service Order`
		WHERE {' AND '.join(conditions)}
		GROUP BY branch, service_category, status
		ORDER BY branch, service_category, status
		""",
		params,
		as_dict=True,
	)

	columns = [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 170},
		{"label": _("Service Category"), "fieldname": "service_category", "fieldtype": "Data", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": _("Orders"), "fieldname": "order_count", "fieldtype": "Int", "width": 100},
		{"label": _("Overdue"), "fieldname": "overdue_count", "fieldtype": "Int", "width": 100},
	]
	return columns, rows
