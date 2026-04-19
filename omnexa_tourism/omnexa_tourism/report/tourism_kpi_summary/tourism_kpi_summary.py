import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	from_date = getdate(filters.get("from_date") or nowdate())
	to_date = getdate(filters.get("to_date") or nowdate())
	if to_date < from_date:
		from_date, to_date = to_date, from_date

	conditions = ["tb.company = %(company)s", "tb.docstatus < 2"]
	values = {
		"company": filters.company,
		"from_date": from_date,
		"to_date": to_date,
	}
	if filters.get("branch"):
		conditions.append("tb.branch = %(branch)s")
		values["branch"] = filters.branch

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		values["allowed_branches"] = tuple(allowed)
		conditions.append("tb.branch in %(allowed_branches)s")

	agg = frappe.db.sql(
		f"""
		SELECT
			COALESCE(SUM(tb.total_room_charges), 0) AS room_revenue,
			COALESCE(SUM(tb.nights), 0) AS room_nights,
			COUNT(tb.name) AS stays
		FROM `tabTourism Booking` tb
		WHERE {' AND '.join(conditions)}
			AND tb.status = 'Checked Out'
			AND tb.check_out_date BETWEEN %(from_date)s AND %(to_date)s
		""",
		values,
		as_dict=True,
	)
	row = agg[0] if agg else {}
	room_revenue = flt(row.get("room_revenue"))
	room_nights = flt(row.get("room_nights"))
	stays = int(row.get("stays") or 0)

	room_count_row = frappe.db.sql(
		"""
		SELECT COUNT(tur.name) AS rooms
		FROM `tabTourism Room Unit` tur
		WHERE tur.docstatus < 2 AND tur.status != 'Disabled' AND tur.company = %(company)s
		"""
		+ (" AND tur.branch = %(branch)s" if values.get("branch") else "")
		+ (" AND tur.branch in %(allowed_branches)s" if values.get("allowed_branches") else ""),
		values,
		as_dict=True,
	)
	rooms = int((room_count_row[0].get("rooms") if room_count_row else 0) or 0)
	period_days = (to_date - from_date).days + 1
	available_room_nights = rooms * max(period_days, 0)

	adr = (room_revenue / room_nights) if room_nights else 0.0
	revpar = (room_revenue / available_room_nights) if available_room_nights else 0.0
	los = (room_nights / stays) if stays else 0.0

	occ_row = frappe.db.sql(
		f"""
		SELECT COALESCE(SUM(tb.nights), 0) AS occupied_room_nights
		FROM `tabTourism Booking` tb
		WHERE {' AND '.join(conditions)}
			AND tb.status != 'Cancelled'
			AND tb.check_in_date BETWEEN %(from_date)s AND %(to_date)s
		""",
		values,
		as_dict=True,
	)
	occupied_room_nights = flt((occ_row[0].get("occupied_room_nights") if occ_row else 0) or 0)
	occupancy = (occupied_room_nights / available_room_nights * 100.0) if available_room_nights else 0.0

	data = [
		{
			"company": filters.company,
			"branch": values.get("branch"),
			"from_date": from_date,
			"to_date": to_date,
			"rooms": rooms,
			"available_room_nights": available_room_nights,
			"occupied_room_nights": occupied_room_nights,
			"occupancy": occupancy,
			"stays": stays,
			"room_nights": room_nights,
			"room_revenue": room_revenue,
			"adr": adr,
			"revpar": revpar,
			"los": los,
		}
	]
	return _columns(), data


def _columns():
	return [
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("From"), "fieldname": "from_date", "fieldtype": "Date", "width": 110},
		{"label": _("To"), "fieldname": "to_date", "fieldtype": "Date", "width": 110},
		{"label": _("Rooms"), "fieldname": "rooms", "fieldtype": "Int", "width": 90},
		{"label": _("Available Room Nights"), "fieldname": "available_room_nights", "fieldtype": "Int", "width": 170},
		{"label": _("Occupied Room Nights"), "fieldname": "occupied_room_nights", "fieldtype": "Float", "width": 170},
		{"label": _("Occupancy %"), "fieldname": "occupancy", "fieldtype": "Percent", "width": 120},
		{"label": _("Stays"), "fieldname": "stays", "fieldtype": "Int", "width": 90},
		{"label": _("Room Nights"), "fieldname": "room_nights", "fieldtype": "Float", "width": 120},
		{"label": _("Room Revenue"), "fieldname": "room_revenue", "fieldtype": "Currency", "width": 130},
		{"label": _("ADR"), "fieldname": "adr", "fieldtype": "Currency", "width": 110},
		{"label": _("RevPAR"), "fieldname": "revpar", "fieldtype": "Currency", "width": 110},
		{"label": _("Avg LOS (nights)"), "fieldname": "los", "fieldtype": "Float", "width": 140},
	]
