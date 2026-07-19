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
	columns = [
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
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Tourism Room Unit", date_field="creation", company=True, branch=True)
	rows = frappe.db.sql(
		f"""
		SELECT
			COUNT(tur.name) AS rooms
		FROM `tabTourism Room Unit`
		WHERE {' AND '.join(conditions)}
		GROUP BY 1
		ORDER BY 1
		""",
		params,
		as_dict=True,
	)
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart