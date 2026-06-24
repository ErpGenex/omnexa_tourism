# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Tourism Package Booking", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Tourism Package Booking",
		fields=['travel_package', 'status', 'package_price'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label": _("Travel Package"), "fieldname": "travel_package", "fieldtype": "Link", "options": "Tourism Travel Package", "width": 220},
		{"label": _("Bookings"), "fieldname": "bookings", "fieldtype": "Int", "width": 90},
		{"label": _("Billed Amount"), "fieldname": "billed_amount", "fieldtype": "Currency", "width": 140},
	], data
