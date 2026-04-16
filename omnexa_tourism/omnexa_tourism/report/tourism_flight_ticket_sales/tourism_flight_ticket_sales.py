import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 160},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Vendor"), "fieldname": "vendor", "fieldtype": "Link", "options": "Tourism Travel Vendor", "width": 180},
		{"label": _("Route"), "fieldname": "route", "fieldtype": "Data", "width": 140},
		{"label": _("Trip Type"), "fieldname": "trip_type", "fieldtype": "Data", "width": 90},
		{"label": _("Cabin"), "fieldname": "cabin_class", "fieldtype": "Data", "width": 110},
		{"label": _("Tickets"), "fieldname": "tickets", "fieldtype": "Int", "width": 80},
		{"label": _("Passengers"), "fieldname": "passengers", "fieldtype": "Int", "width": 100},
		{"label": _("Base Fare"), "fieldname": "base_fare", "fieldtype": "Currency", "width": 120},
		{"label": _("Taxes"), "fieldname": "taxes", "fieldtype": "Currency", "width": 100},
		{"label": _("Fees"), "fieldname": "fees", "fieldtype": "Currency", "width": 100},
		{"label": _("Ticket Total"), "fieldname": "total_price", "fieldtype": "Currency", "width": 130},
		{"label": _("Markup"), "fieldname": "markup_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Billed Amount"), "fieldname": "billed_amount", "fieldtype": "Currency", "width": 130},
	]

	data = _get_data(filters)
	return columns, data


def _get_data(filters):
	conditions = ["fb.status = 'Billed'"]
	values = {}

	if filters.get("from_date"):
		conditions.append("DATE(fb.departure_datetime) >= %(from_date)s")
		values["from_date"] = getdate(filters["from_date"])
	if filters.get("to_date"):
		conditions.append("DATE(fb.departure_datetime) <= %(to_date)s")
		values["to_date"] = getdate(filters["to_date"])
	if filters.get("company"):
		conditions.append("fb.company = %(company)s")
		values["company"] = filters["company"]
	if filters.get("branch"):
		conditions.append("fb.branch = %(branch)s")
		values["branch"] = filters["branch"]
	if filters.get("vendor"):
		conditions.append("fb.vendor = %(vendor)s")
		values["vendor"] = filters["vendor"]

	where_clause = " AND ".join(conditions)
	return frappe.db.sql(
		f"""
		SELECT
			DATE(fb.departure_datetime) AS posting_date,
			fb.company,
			fb.branch,
			fb.vendor,
			CONCAT(COALESCE(fb.from_airport,''), ' → ', COALESCE(fb.to_airport,'')) AS route,
			fb.trip_type,
			fb.cabin_class,
			COUNT(*) AS tickets,
			SUM(COALESCE(fb.passengers, 0)) AS passengers,
			SUM(COALESCE(fb.base_fare, 0)) AS base_fare,
			SUM(COALESCE(fb.taxes, 0)) AS taxes,
			SUM(COALESCE(fb.fees, 0)) AS fees,
			SUM(COALESCE(fb.total_price, 0)) AS total_price,
			SUM(COALESCE(fb.markup_amount, 0)) AS markup_amount,
			SUM(COALESCE(fb.price, 0)) AS billed_amount
		FROM `tabTourism Flight Booking` fb
		WHERE {where_clause}
		GROUP BY
			DATE(fb.departure_datetime), fb.company, fb.branch, fb.vendor,
			fb.from_airport, fb.to_airport, fb.trip_type, fb.cabin_class
		ORDER BY posting_date DESC, fb.vendor ASC
		""",
		values,
		as_dict=True,
	)

