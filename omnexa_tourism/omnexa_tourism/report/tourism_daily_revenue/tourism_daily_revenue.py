import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt, nowdate


def execute(filters=None):
	filters = filters or {}

	report_date = filters.get("date") or nowdate()
	branch = filters.get("branch")

	branch_clause = ""
	params = {"report_date": report_date}
	if branch:
		branch_clause = "AND tb.branch = %(branch)s"
		params["branch"] = branch

	rows = frappe.db.sql(
		"""
		SELECT
			tb.branch,
			tb.check_out_date AS report_date,
			COALESCE(SUM(tb.total_room_charges), 0) AS revenue,
			COUNT(tb.name) AS stays
		FROM `tabTourism Booking` tb
		WHERE tb.docstatus < 2
			AND tb.status = 'Checked Out'
			AND tb.check_out_date = %(report_date)s
			{branch_clause}
		GROUP BY tb.branch, tb.check_out_date
		ORDER BY tb.branch ASC
		""".format(branch_clause=branch_clause),
		params,
		as_dict=True,
	)

	columns = [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 180},
		{"label": _("Date"), "fieldname": "report_date", "fieldtype": "Date", "width": 120},
		{"label": _("Room Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 150},
		{"label": _("Stays"), "fieldname": "stays", "fieldtype": "Int", "width": 90},
	]

	data = []
	for row in rows:
		data.append(
			{
				"branch": row.get("branch"),
				"report_date": row.get("report_date"),
				"revenue": flt(row.get("revenue")),
				"stays": int(row.get("stays") or 0),
			}
		)
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart