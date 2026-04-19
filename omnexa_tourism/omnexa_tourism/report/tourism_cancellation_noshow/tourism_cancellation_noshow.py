import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["tb.company = %(company)s", "tb.docstatus < 2"]
	values = {"company": filters.company, "today": getdate(nowdate())}
	if filters.get("branch"):
		conditions.append("tb.branch = %(branch)s")
		values["branch"] = filters.branch
	if filters.get("from_date"):
		conditions.append("tb.check_in_date >= %(from_date)s")
		values["from_date"] = getdate(filters.from_date)
	if filters.get("to_date"):
		conditions.append("tb.check_in_date <= %(to_date)s")
		values["to_date"] = getdate(filters.to_date)

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		values["allowed_branches"] = tuple(allowed)
		conditions.append("tb.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			tb.booking_channel,
			SUM(CASE WHEN tb.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
			SUM(CASE WHEN tb.status = 'Confirmed' AND tb.check_in_date < %(today)s THEN 1 ELSE 0 END) AS no_show,
			COUNT(tb.name) AS total_bookings
		FROM `tabTourism Booking` tb
		WHERE {' AND '.join(conditions)}
		GROUP BY tb.booking_channel
		ORDER BY total_bookings DESC, tb.booking_channel ASC
		""",
		values,
		as_dict=True,
	)
	for row in data:
		total = int(row.get("total_bookings") or 0)
		cancelled = int(row.get("cancelled") or 0)
		no_show = int(row.get("no_show") or 0)
		row.cancel_rate = (flt(cancelled) / total * 100.0) if total else 0.0
		row.no_show_rate = (flt(no_show) / total * 100.0) if total else 0.0
	return _columns(), data


def _columns():
	return [
		{"label": _("Channel"), "fieldname": "booking_channel", "fieldtype": "Data", "width": 140},
		{"label": _("Total Bookings"), "fieldname": "total_bookings", "fieldtype": "Int", "width": 120},
		{"label": _("Cancelled"), "fieldname": "cancelled", "fieldtype": "Int", "width": 100},
		{"label": _("Cancel %"), "fieldname": "cancel_rate", "fieldtype": "Percent", "width": 100},
		{"label": _("No-show"), "fieldname": "no_show", "fieldtype": "Int", "width": 100},
		{"label": _("No-show %"), "fieldname": "no_show_rate", "fieldtype": "Percent", "width": 110},
	]
