# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import json

import frappe
from frappe import _


PALETTE = '{"colors": ["#2490ef", "#ffa00a", "#743ee2", "#5e64ff", "#39e4a5", "#fc6164"]}'


def _upsert_dashboard_chart(doc_dict: dict) -> None:
	name = doc_dict["chart_name"]
	if frappe.db.exists("Dashboard Chart", name):
		return
	doc = frappe.new_doc("Dashboard Chart")
	doc.update(doc_dict)
	doc.insert(ignore_permissions=True)


def _upsert_number_card(doc_dict: dict) -> str:
	# Keep stable identity using label as primary key
	label = doc_dict["label"]
	name = frappe.db.get_value("Number Card", {"label": label}, "name")
	if name:
		return name
	doc = frappe.new_doc("Number Card")
	doc.update(doc_dict)
	doc.insert(ignore_permissions=True)
	return doc.name


def _ensure_front_office_widgets():
	# Charts
	_upsert_dashboard_chart(
		{
			"chart_name": "TOUR · Booking Status Mix",
			"chart_type": "Group By",
			"document_type": "Tourism Booking",
			"filters_json": json.dumps([["docstatus", "<", 2]]),
			"group_by_based_on": "status",
			"group_by_type": "Count",
			"number_of_groups": 10,
			"type": "Donut",
			"is_public": 1,
			"custom_options": PALETTE,
		}
	)
	_upsert_dashboard_chart(
		{
			"chart_name": "TOUR · Booking Channels",
			"chart_type": "Group By",
			"document_type": "Tourism Booking",
			"filters_json": json.dumps([["docstatus", "<", 2]]),
			"group_by_based_on": "booking_channel",
			"group_by_type": "Count",
			"number_of_groups": 10,
			"type": "Bar",
			"is_public": 1,
			"custom_options": PALETTE,
		}
	)
	_upsert_dashboard_chart(
		{
			"chart_name": "TOUR · Arrivals Trend",
			"chart_type": "Count",
			"document_type": "Tourism Booking",
			"filters_json": json.dumps([["docstatus", "<", 2]]),
			"timeseries": 1,
			"based_on": "check_in_date",
			"timespan": "Last Month",
			"time_interval": "Daily",
			"type": "Line",
			"is_public": 1,
			"custom_options": PALETTE,
		}
	)
	_upsert_dashboard_chart(
		{
			"chart_name": "TOUR · Service Orders Status",
			"chart_type": "Group By",
			"document_type": "Tourism Service Order",
			"filters_json": json.dumps([["docstatus", "<", 2]]),
			"group_by_based_on": "status",
			"group_by_type": "Count",
			"number_of_groups": 10,
			"type": "Bar",
			"is_public": 1,
			"custom_options": PALETTE,
		}
	)

	# Number cards (dynamic via custom whitelisted methods)
	nc_names = []
	for label, method in (
		("TOUR KPI — Arrivals Today", "omnexa_tourism.front_office_kpis.kpi_arrivals_today"),
		("TOUR KPI — Departures Today", "omnexa_tourism.front_office_kpis.kpi_departures_today"),
		("TOUR KPI — In House", "omnexa_tourism.front_office_kpis.kpi_in_house"),
		("TOUR KPI — Pending Web Requests", "omnexa_tourism.front_office_kpis.kpi_pending_web_requests"),
		("TOUR KPI — Open Service Orders", "omnexa_tourism.front_office_kpis.kpi_open_service_orders"),
		("TOUR KPI — Outstanding Folios", "omnexa_tourism.front_office_kpis.kpi_outstanding_folios"),
	):
		nc_names.append(
			_upsert_number_card(
				{
					"label": label,
					"type": "Custom",
					"method": method,
					"is_public": 1,
					"show_percentage_stats": 0,
				}
			)
		)
	return nc_names


def _ensure_workspace():
	name = "Hotel Front Office"
	# Keep workspace placement and icon stable in sidebar.
	desired = {
		"title": name,
		"label": name,
		"module": "Omnexa Tourism",
		"icon": "map",
		"public": 1,
		"sequence_id": 7.6,  # Tourism is 7.5; keep this immediately after it.
	}
	if frappe.db.exists("Workspace", name):
		ws = frappe.get_doc("Workspace", name)
		changed = False
		for key, value in desired.items():
			if ws.get(key) != value:
				ws.set(key, value)
				changed = True
		if changed:
			ws.save(ignore_permissions=True)
		return ws

	ws = frappe.new_doc("Workspace")
	ws.update(desired)
	ws.content = "[]"
	ws.insert(ignore_permissions=True)
	return ws


def ensure_hotel_front_office_workspace():
	"""Create/refresh a dedicated hotel front-office workspace with charts, KPIs, reports and shortcuts."""
	if not frappe.db.exists("DocType", "Workspace"):
		return

	nc_names = _ensure_front_office_widgets()
	ws = _ensure_workspace()

	# Attach widgets (idempotent)
	existing_charts = {row.chart_name for row in (ws.charts or [])}
	for chart_name, lbl in (
		("TOUR · Booking Status Mix", _("Booking status mix")),
		("TOUR · Booking Channels", _("Booking channels")),
		("TOUR · Arrivals Trend", _("Arrivals trend")),
		("TOUR · Service Orders Status", _("Service orders status")),
	):
		if frappe.db.exists("Dashboard Chart", chart_name) and chart_name not in existing_charts:
			ws.append("charts", {"chart_name": chart_name, "label": lbl})

	existing_cards = {row.number_card_name for row in (ws.number_cards or [])}
	for nc_name in nc_names:
		if nc_name and nc_name not in existing_cards:
			ws.append("number_cards", {"number_card_name": nc_name})

	# Links (card breaks + links)
	existing_links = {(row.get("type"), row.get("label"), row.get("link_type"), row.get("link_to")) for row in (ws.links or [])}
	def add_card(label: str):
		key = ("Card Break", label, None, None)
		if key in existing_links:
			return
		ws.append("links", {"type": "Card Break", "label": label, "hidden": 0, "onboard": 0, "link_count": 0})
		existing_links.add(key)

	def add_link(label: str, link_type: str, link_to: str, is_query_report: int = 0):
		key = ("Link", label, link_type, link_to)
		if key in existing_links:
			return
		ws.append(
			"links",
			{
				"type": "Link",
				"label": label,
				"link_type": link_type,
				"link_to": link_to,
				"is_query_report": is_query_report,
				"hidden": 0,
				"onboard": 0,
				"link_count": 0,
			},
		)
		existing_links.add(key)

	add_card("Front Office — Bookings")
	add_link("Booking", "DocType", "Tourism Booking")
	add_link("Online Booking Request", "DocType", "Tourism Online Booking Request")
	add_link("Guest Folio", "DocType", "Tourism Guest Folio")
	add_link("Charge Entry", "DocType", "Tourism Charge Entry")

	add_card("Front Office — Facilities & services")
	add_link("Service Order", "DocType", "Tourism Service Order")
	add_link("Restaurant Reservation", "DocType", "Tourism Restaurant Reservation")
	add_link("Beach Booking", "DocType", "Tourism Beach Booking")
	add_link("Activity Booking", "DocType", "Tourism Activity Booking")
	add_link("Housekeeping Task", "DocType", "Tourism Housekeeping Task")

	add_card("Front Office — POS & Billing")
	add_link("Restaurant Order", "DocType", "Restaurant Order")
	add_link("Sales Invoice", "DocType", "Sales Invoice")
	add_link("Journal Entry", "DocType", "Journal Entry")

	add_card("Front Office — Reports")
	for rpt in (
		"Tourism Front Office Arrivals Departures",
		"Tourism Service Order Backlog",
		"Tourism POS Sales Summary",
		"Tourism Occupancy",
		"Tourism Booking Status Summary",
		"Tourism Cancellation NoShow",
		"Tourism Guest Folio Outstanding",
		"Tourism Daily Revenue",
		"Tourism KPI Summary",
		"Tourism Housekeeping Performance",
		"Tourism Channel Performance",
		"Tourism Lead Time Analysis",
		"Tourism Room Type Performance",
		"Tourism Service Profitability",
		"Tourism Package Profitability",
		"Tourism Flight Ticket Sales",
	):
		if frappe.db.exists("Report", rpt):
			add_link(rpt.replace("Tourism ", ""), "Report", rpt, is_query_report=1)

	ws.save(ignore_permissions=True)

