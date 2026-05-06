# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe.utils import nowdate


def get_notification_config():
	"""Desk notification badges for hotel front/back office workflows."""
	today = nowdate()

	def _count(doctype: str, filters: dict) -> int:
		try:
			return int(frappe.db.count(doctype, filters=filters) or 0)
		except Exception:
			return 0

	def _booking_exceptions() -> int:
		# Operational control for international front-office standards:
		# - No-show risk: confirmed bookings with check-in date in the past
		# - Late checkout risk: checked-in bookings with check-out date in the past
		no_show = _count(
			"Tourism Booking",
			{"status": "Confirmed", "check_in_date": ["<", today], "docstatus": ["<", 2]},
		)
		late_checkout = _count(
			"Tourism Booking",
			{"status": "Checked In", "check_out_date": ["<", today], "docstatus": ["<", 2]},
		)
		return no_show + late_checkout

	return {
		"for_doctype": {
			# Front office
			"Tourism Online Booking Request": lambda: _count(
				"Tourism Online Booking Request",
				{"status": ["in", ["New", "In Progress"]], "docstatus": ["<", 2]},
			),
			"Tourism Booking": lambda: (
				_count(
					"Tourism Booking",
					{
						"check_in_date": today,
						"status": ["in", ["Confirmed"]],
						"docstatus": ["<", 2],
					},
				)
				+ _count(
					"Tourism Booking",
					{
						"check_out_date": today,
						"status": ["in", ["Checked In"]],
						"docstatus": ["<", 2],
					},
				)
				+ _booking_exceptions()
			),
			"Tourism Guest Folio": lambda: _count(
				"Tourism Guest Folio",
				{"status": "Open", "docstatus": ["<", 2], "balance_due": [">", 0]},
			),
			"Tourism Service Order": lambda: _count(
				"Tourism Service Order",
				{"status": ["in", ["Ordered", "In Progress"]], "docstatus": ["<", 2]},
			),
			"Tourism Housekeeping Task": lambda: _count(
				"Tourism Housekeeping Task",
				{"status": ["in", ["Pending", "In Progress"]], "scheduled_date": today, "docstatus": ["<", 2]},
			),
		}
	}

