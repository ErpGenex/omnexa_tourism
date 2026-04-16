import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	flt_map = {"docstatus": ["<", 2]}
	if filters.get("company"):
		flt_map["company"] = filters["company"]
	if filters.get("branch"):
		flt_map["branch"] = filters["branch"]
	if filters.get("travel_package"):
		flt_map["travel_package"] = filters["travel_package"]

	columns = [
		{"label": "Travel Package", "fieldname": "travel_package", "fieldtype": "Link", "options": "Tourism Travel Package", "width": 220},
		{"label": "Bookings", "fieldname": "bookings", "fieldtype": "Int", "width": 90},
		{"label": "Billed Amount", "fieldname": "billed_amount", "fieldtype": "Currency", "width": 140},
	]

	rows = frappe.get_all(
		"Tourism Package Booking",
		fields=["travel_package", "status", "package_price"],
		filters=flt_map,
		limit_page_length=5000,
	)

	agg = {}
	for r in rows:
		pkg = r.get("travel_package")
		if pkg not in agg:
			agg[pkg] = {"travel_package": pkg, "bookings": 0, "billed_amount": 0.0}
		agg[pkg]["bookings"] += 1
		if r.get("status") == "Billed":
			agg[pkg]["billed_amount"] += flt(r.get("package_price"))

	data = [agg[k] for k in sorted(agg)]
	return columns, data

