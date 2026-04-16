import frappe
from frappe.utils import flt, nowdate


def execute(filters=None):
	filters = filters or {}

	plan_date = filters.get("date") or nowdate()
	branch = filters.get("branch")

	params = {"plan_date": plan_date}
	branch_clause_booking = ""
	branch_clause_task = ""
	if branch:
		branch_clause_booking = "AND tb.branch = %(branch)s"
		branch_clause_task = "AND tkt.branch = %(branch)s"
		params["branch"] = branch

	# Rooms revenue from already-created sales invoice trigger (based on booking status).
	# For now we treat service cost as unknown, so we keep it 0.
	rows = frappe.db.sql(
		f"""
		SELECT
			tb.branch,
			tb.check_out_date AS report_date,
			COALESCE(SUM(tb.total_room_charges), 0) AS room_revenue,
			COUNT(tb.name) AS room_stays
		FROM `tabTourism Booking` tb
		WHERE tb.docstatus < 2
			AND tb.status = 'Checked Out'
			AND tb.check_out_date = %(plan_date)s
			{branch_clause_booking}
		GROUP BY tb.branch, tb.check_out_date
		ORDER BY tb.branch ASC
		""",
		params,
		as_dict=True,
	)

	tasks = frappe.db.sql(
		f"""
		SELECT
			tkt.branch,
			tkt.scheduled_date AS report_date,
			SUM(CASE WHEN tkt.status IN ('Completed', 'Verified') THEN 1 ELSE 0 END) AS completed_tasks
		FROM `tabTourism Housekeeping Task` tkt
		WHERE tkt.docstatus < 2
			AND tkt.scheduled_date = %(plan_date)s
			{branch_clause_task}
		GROUP BY tkt.branch, tkt.scheduled_date
		ORDER BY tkt.branch ASC
		""",
		params,
		as_dict=True,
	)

	tasks_map = {}
	for t in tasks or []:
		tasks_map[(t.get("branch"), t.get("report_date"))] = int(t.get("completed_tasks") or 0)

	columns = [
		{"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 180},
		{"label": "Date", "fieldname": "report_date", "fieldtype": "Date", "width": 120},
		{"label": "Room Revenue", "fieldname": "room_revenue", "fieldtype": "Currency", "width": 150},
		{"label": "Service Tasks (Completed)", "fieldname": "completed_tasks", "fieldtype": "Int", "width": 220},
		{"label": "Service Cost", "fieldname": "service_cost", "fieldtype": "Currency", "width": 140},
		{"label": "Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 120},
		{"label": "Room Stays", "fieldname": "room_stays", "fieldtype": "Int", "width": 120},
	]

	data = []
	for r in rows or []:
		branch_name = r.get("branch")
		date_val = r.get("report_date")
		room_revenue = flt(r.get("room_revenue"))
		completed_tasks = tasks_map.get((branch_name, date_val), 0)
		service_cost = 0.0
		profit = room_revenue - service_cost
		data.append(
			{
				"branch": branch_name,
				"report_date": date_val,
				"room_revenue": room_revenue,
				"completed_tasks": completed_tasks,
				"service_cost": service_cost,
				"profit": profit,
				"room_stays": int(r.get("room_stays") or 0),
			}
		)

	return columns, data

