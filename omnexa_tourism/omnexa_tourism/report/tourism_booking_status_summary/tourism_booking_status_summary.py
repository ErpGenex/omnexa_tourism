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
			status,
			COUNT(name) AS booking_count,
			COALESCE(SUM(nights), 0) AS total_nights,
			COALESCE(SUM(total_room_charges), 0) AS total_room_revenue
		FROM `tabTourism Booking`
		WHERE {' AND '.join(conditions)}
		GROUP BY status
		ORDER BY status
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row.total_nights = flt(row.total_nights)
		row.total_room_revenue = flt(row.total_room_revenue)
	return _columns(), data


def _columns():
	return [
		{"label": _("Booking Status"), "fieldname": "status", "fieldtype": "Data", "width": 160},
		{"label": _("Bookings"), "fieldname": "booking_count", "fieldtype": "Int", "width": 120},
		{"label": _("Total Nights"), "fieldname": "total_nights", "fieldtype": "Float", "width": 130},
		{"label": _("Room Revenue"), "fieldname": "total_room_revenue", "fieldtype": "Currency", "width": 140},
	]
