# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe.utils import nowdate


def _count(doctype: str, filters: dict) -> int:
	return int(frappe.db.count(doctype, filters=filters) or 0)


@frappe.whitelist()
def kpi_arrivals_today():
	"""Confirmed bookings with check-in = today."""
	today = nowdate()
	value = _count(
		"Tourism Booking",
		{"check_in_date": today, "status": "Confirmed", "docstatus": ["<", 2]},
	)
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Tourism Booking", "List"],
		"route_options": {"check_in_date": today, "status": "Confirmed"},
	}


@frappe.whitelist()
def kpi_departures_today():
	"""Checked-in bookings with check-out = today."""
	today = nowdate()
	value = _count(
		"Tourism Booking",
		{"check_out_date": today, "status": "Checked In", "docstatus": ["<", 2]},
	)
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Tourism Booking", "List"],
		"route_options": {"check_out_date": today, "status": "Checked In"},
	}


@frappe.whitelist()
def kpi_in_house():
	"""Bookings currently in-house (Checked In)."""
	value = _count("Tourism Booking", {"status": "Checked In", "docstatus": ["<", 2]})
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Tourism Booking", "List"],
		"route_options": {"status": "Checked In"},
	}


@frappe.whitelist()
def kpi_pending_web_requests():
	value = _count(
		"Tourism Online Booking Request",
		{"status": ["in", ["New", "In Progress"]], "docstatus": ["<", 2]},
	)
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Tourism Online Booking Request", "List"],
		"route_options": {"status": ["in", ["New", "In Progress"]]},
	}


@frappe.whitelist()
def kpi_open_service_orders():
	value = _count("Tourism Service Order", {"status": ["in", ["Ordered", "In Progress"]], "docstatus": ["<", 2]})
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Tourism Service Order", "List"],
		"route_options": {"status": ["in", ["Ordered", "In Progress"]]},
	}


@frappe.whitelist()
def kpi_outstanding_folios():
	value = _count("Tourism Guest Folio", {"status": "Open", "balance_due": [">", 0], "docstatus": ["<", 2]})
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Tourism Guest Folio", "List"],
		"route_options": {"status": "Open", "balance_due": [">", 0]},
	}

