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

	arrivals = frappe.db.sql(
		f"""
		SELECT branch, status, COUNT(name) AS arrivals
		FROM `tabTourism Booking`
		WHERE {' AND '.join(conditions)} AND check_in_date = %(target_date)s
		GROUP BY branch, status
		""",
		params,
		as_dict=True,
	)
	departures = frappe.db.sql(
		f"""
		SELECT branch, status, COUNT(name) AS departures
		FROM `tabTourism Booking`
		WHERE {' AND '.join(conditions)} AND check_out_date = %(target_date)s
		GROUP BY branch, status
		""",
		params,
		as_dict=True,
	)

	index = {}
	for row in arrivals:
		k = (row.branch or "", row.status or "")
		index.setdefault(k, {"branch": row.branch, "status": row.status, "arrivals": 0, "departures": 0})
		index[k]["arrivals"] = int(row.arrivals or 0)
	for row in departures:
		k = (row.branch or "", row.status or "")
		index.setdefault(k, {"branch": row.branch, "status": row.status, "arrivals": 0, "departures": 0})
		index[k]["departures"] = int(row.departures or 0)

	data = list(index.values())
	for d in data:
		d["net_movement"] = int(d["arrivals"] or 0) - int(d["departures"] or 0)
		d["target_date"] = target_date
	data.sort(key=lambda x: (x.get("branch") or "", x.get("status") or ""))

	columns = [
		{"label": _("Date"), "fieldname": "target_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 180},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 140},
		{"label": _("Arrivals"), "fieldname": "arrivals", "fieldtype": "Int", "width": 100},
		{"label": _("Departures"), "fieldname": "departures", "fieldtype": "Int", "width": 100},
		{"label": _("Net"), "fieldname": "net_movement", "fieldtype": "Int", "width": 90},
	]
	return columns, data
