# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe.utils import nowdate


def _count(doctype: str, filters: dict) -> int:
	try:
		return int(frappe.db.count(doctype, filters=filters) or 0)
	except Exception:
		return 0


def get_pending_online_requests():
	return _count(
		"Tourism Online Booking Request",
		{"status": ["in", ["New", "In Progress"]], "docstatus": ["<", 2]},
	)


def get_booking_operational_alerts():
	today = nowdate()
	arrivals = _count(
		"Tourism Booking",
		{
			"check_in_date": today,
			"status": ["in", ["Confirmed"]],
			"docstatus": ["<", 2],
		},
	)
	departures = _count(
		"Tourism Booking",
		{
			"check_out_date": today,
			"status": ["in", ["Checked In"]],
			"docstatus": ["<", 2],
		},
	)
	no_show = _count(
		"Tourism Booking",
		{"status": "Confirmed", "check_in_date": ["<", today], "docstatus": ["<", 2]},
	)
	late_checkout = _count(
		"Tourism Booking",
		{"status": "Checked In", "check_out_date": ["<", today], "docstatus": ["<", 2]},
	)
	return arrivals + departures + no_show + late_checkout


def get_open_guest_folios_due():
	return _count(
		"Tourism Guest Folio",
		{"status": "Open", "docstatus": ["<", 2], "balance_due": [">", 0]},
	)


def get_open_service_orders():
	return _count(
		"Tourism Service Order",
		{"status": ["in", ["Ordered", "In Progress"]], "docstatus": ["<", 2]},
	)


def get_housekeeping_today_pending():
	today = nowdate()
	return _count(
		"Tourism Housekeeping Task",
		{"status": ["in", ["Pending", "In Progress"]], "scheduled_date": today, "docstatus": ["<", 2]},
	)


def get_notification_config():
	"""Desk notification badges for hotel front/back office workflows."""

	return {
		"for_doctype": {
			# Front office
			"Tourism Online Booking Request": "omnexa_tourism.notifications.get_pending_online_requests",
			"Tourism Booking": "omnexa_tourism.notifications.get_booking_operational_alerts",
			"Tourism Guest Folio": "omnexa_tourism.notifications.get_open_guest_folios_due",
			"Tourism Service Order": "omnexa_tourism.notifications.get_open_service_orders",
			"Tourism Housekeeping Task": "omnexa_tourism.notifications.get_housekeeping_today_pending",
		}
	}

