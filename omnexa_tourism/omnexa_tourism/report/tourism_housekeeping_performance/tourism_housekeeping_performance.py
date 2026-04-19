import frappe
from frappe import _
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["company = %(company)s"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("scheduled_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("scheduled_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			branch,
			status,
			COUNT(name) AS task_count
		FROM `tabTourism Housekeeping Task`
		WHERE {' AND '.join(conditions)}
		GROUP BY branch, status
		ORDER BY branch ASC, status ASC
		""",
		filters,
		as_dict=True,
	)
	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 150},
		{"label": _("Task Status"), "fieldname": "status", "fieldtype": "Data", "width": 140},
		{"label": _("Tasks"), "fieldname": "task_count", "fieldtype": "Int", "width": 100},
	]
