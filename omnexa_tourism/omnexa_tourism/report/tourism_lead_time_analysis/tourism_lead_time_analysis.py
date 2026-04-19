import frappe
from frappe import _
from frappe.utils import flt, getdate
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["tb.company = %(company)s", "tb.docstatus < 2"]
	values = {"company": filters.company}
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
			COUNT(tb.name) AS booking_count,
			AVG(DATEDIFF(tb.check_in_date, DATE(tb.creation))) AS avg_lead_days,
			AVG(tb.nights) AS avg_los
		FROM `tabTourism Booking` tb
		WHERE {' AND '.join(conditions)}
		GROUP BY tb.booking_channel
		ORDER BY booking_count DESC, tb.booking_channel ASC
		""",
		values,
		as_dict=True,
	)
	for row in data:
		row.avg_lead_days = flt(row.avg_lead_days)
		row.avg_los = flt(row.avg_los)
	return _columns(), data


def _columns():
	return [
		{"label": _("Channel"), "fieldname": "booking_channel", "fieldtype": "Data", "width": 140},
		{"label": _("Bookings"), "fieldname": "booking_count", "fieldtype": "Int", "width": 100},
		{"label": _("Avg Lead Time (days)"), "fieldname": "avg_lead_days", "fieldtype": "Float", "width": 160},
		{"label": _("Avg LOS (nights)"), "fieldname": "avg_los", "fieldtype": "Float", "width": 140},
	]
