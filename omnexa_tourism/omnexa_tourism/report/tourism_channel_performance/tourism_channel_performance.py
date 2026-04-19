import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["company = %(company)s", "docstatus < 2"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("check_in_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("check_in_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			booking_channel,
			COUNT(name) AS booking_count,
			COALESCE(SUM(nights), 0) AS room_nights,
			COALESCE(SUM(total_room_charges), 0) AS revenue
		FROM `tabTourism Booking`
		WHERE {' AND '.join(conditions)}
		GROUP BY booking_channel
		ORDER BY revenue DESC, booking_channel ASC
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row.room_nights = flt(row.room_nights)
		row.revenue = flt(row.revenue)
	return _columns(), data


def _columns():
	return [
		{"label": _("Channel"), "fieldname": "booking_channel", "fieldtype": "Data", "width": 140},
		{"label": _("Bookings"), "fieldname": "booking_count", "fieldtype": "Int", "width": 110},
		{"label": _("Room Nights"), "fieldname": "room_nights", "fieldtype": "Float", "width": 120},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 140},
	]
