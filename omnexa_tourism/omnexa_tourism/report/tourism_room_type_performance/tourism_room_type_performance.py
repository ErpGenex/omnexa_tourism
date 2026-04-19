import frappe
from frappe import _
from frappe.utils import flt, getdate
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["tb.company = %(company)s", "tb.docstatus < 2", "tb.status != 'Cancelled'"]
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
			tur.room_type AS room_type,
			COUNT(tb.name) AS booking_count,
			COALESCE(SUM(tb.nights), 0) AS room_nights,
			COALESCE(SUM(tb.total_room_charges), 0) AS revenue
		FROM `tabTourism Booking` tb
		LEFT JOIN `tabTourism Room Unit` tur ON tur.name = tb.unit
		WHERE {' AND '.join(conditions)}
		GROUP BY tur.room_type
		ORDER BY revenue DESC
		""",
		values,
		as_dict=True,
	)
	for row in data:
		row.room_nights = flt(row.room_nights)
		row.revenue = flt(row.revenue)
		row.adr = (row.revenue / row.room_nights) if row.room_nights else 0.0
	return _columns(), data


def _columns():
	return [
		{"label": _("Room Type"), "fieldname": "room_type", "fieldtype": "Link", "options": "Tourism Room Type", "width": 160},
		{"label": _("Bookings"), "fieldname": "booking_count", "fieldtype": "Int", "width": 100},
		{"label": _("Room Nights"), "fieldname": "room_nights", "fieldtype": "Float", "width": 120},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 130},
		{"label": _("ADR"), "fieldname": "adr", "fieldtype": "Currency", "width": 110},
	]
