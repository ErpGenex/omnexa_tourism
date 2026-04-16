import frappe
from frappe.utils import flt, nowdate


def execute(filters=None):
	filters = filters or {}

	occ_date = filters.get("date") or nowdate()
	branch = filters.get("branch")

	branch_unit_clause = ""
	branch_booking_clause = ""
	params = {"occ_date": occ_date}

	if branch:
		branch_unit_clause = "AND tur.branch = %(branch)s"
		branch_booking_clause = "AND tb.branch = %(branch)s"
		params["branch"] = branch

	total_rooms = frappe.db.sql(
		f"""
		SELECT
			COUNT(tur.name) AS total_rooms
		FROM `tabTourism Room Unit` tur
		WHERE tur.docstatus < 2
			AND tur.status != 'Disabled'
			{branch_unit_clause}
		""",
		params,
		as_dict=True,
	)

	occupied_rooms = frappe.db.sql(
		f"""
		SELECT
			COUNT(DISTINCT tb.unit) AS occupied_rooms
		FROM `tabTourism Booking` tb
		WHERE tb.docstatus < 2
			AND tb.status != 'Cancelled'
			AND tb.check_in_date <= %(occ_date)s
			AND tb.check_out_date > %(occ_date)s
			{branch_booking_clause}
		""",
		params,
		as_dict=True,
	)

	total = int(total_rooms[0].get("total_rooms") if total_rooms else 0)
	occ = int(occupied_rooms[0].get("occupied_rooms") if occupied_rooms else 0)
	occupancy_rate = (flt(occ) / total * 100.0) if total else 0.0

	columns = [
		{"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
		{"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 180},
		{"label": "Total Rooms", "fieldname": "total_rooms", "fieldtype": "Int", "width": 140},
		{"label": "Occupied Rooms", "fieldname": "occupied_rooms", "fieldtype": "Int", "width": 160},
		{"label": "Occupancy %", "fieldname": "occupancy_rate", "fieldtype": "Percent", "width": 140},
	]

	data = [
		{
			"date": occ_date,
			"branch": branch,
			"total_rooms": total,
			"occupied_rooms": occ,
			"occupancy_rate": occupancy_rate,
		}
	]

	return columns, data

