# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe.utils import add_days, add_to_date, nowdate


def hourly():
	"""Hourly SLA guards for front-office operations."""
	_create_hourly_sla_todos()


def daily():
	"""Daily SLA controls for front/back office handoffs."""
	_create_daily_sla_todos()


def _create_todo(subject: str, reference_type: str, reference_name: str, allocated_to: str | None = None):
	allocated_to = allocated_to or "Administrator"
	exists = frappe.db.exists(
		"ToDo",
		{
			"status": "Open",
			"allocated_to": allocated_to,
			"reference_type": reference_type,
			"reference_name": reference_name,
			"description": subject,
		},
	)
	if exists:
		return
	frappe.get_doc(
		{
			"doctype": "ToDo",
			"description": subject,
			"allocated_to": allocated_to,
			"reference_type": reference_type,
			"reference_name": reference_name,
			"status": "Open",
		}
	).insert(ignore_permissions=True)


def _create_daily_sla_todos():
	today = nowdate()
	no_show_rows = frappe.get_all(
		"Tourism Booking",
		filters={"status": "Confirmed", "check_in_date": ["<", today], "docstatus": ["<", 2]},
		fields=["name", "booking_owner", "customer", "branch", "check_in_date"],
		limit_page_length=200,
	)
	for row in no_show_rows:
		_create_todo(
			subject=f"[Tourism SLA] No-show risk: booking {row.name} was due check-in on {row.check_in_date}.",
			reference_type="Tourism Booking",
			reference_name=row.name,
			allocated_to=row.booking_owner,
		)

	late_checkout_rows = frappe.get_all(
		"Tourism Booking",
		filters={"status": "Checked In", "check_out_date": ["<", today], "docstatus": ["<", 2]},
		fields=["name", "booking_owner", "customer", "branch", "check_out_date"],
		limit_page_length=200,
	)
	for row in late_checkout_rows:
		_create_todo(
			subject=f"[Tourism SLA] Late checkout: booking {row.name} passed checkout date {row.check_out_date}.",
			reference_type="Tourism Booking",
			reference_name=row.name,
			allocated_to=row.booking_owner,
		)

	hk_rows = frappe.get_all(
		"Tourism Housekeeping Task",
		filters={"status": ["in", ["Pending", "In Progress"]], "scheduled_date": ["<", today], "docstatus": ["<", 2]},
		fields=["name", "task_owner", "unit", "scheduled_date"],
		limit_page_length=300,
	)
	for row in hk_rows:
		_create_todo(
			subject=f"[Tourism SLA] Housekeeping overdue: task {row.name} scheduled for {row.scheduled_date}.",
			reference_type="Tourism Housekeeping Task",
			reference_name=row.name,
			allocated_to=row.task_owner,
		)

	aged_folios = frappe.get_all(
		"Tourism Guest Folio",
		filters={"status": "Open", "balance_due": [">", 0], "folio_date": ["<=", add_days(today, -3)], "docstatus": ["<", 2]},
		fields=["name", "booking", "customer", "balance_due"],
		limit_page_length=200,
	)
	for row in aged_folios:
		_create_todo(
			subject=f"[Tourism SLA] Outstanding folio: {row.name} has due balance {row.balance_due}.",
			reference_type="Tourism Guest Folio",
			reference_name=row.name,
			allocated_to=None,
		)


def _create_hourly_sla_todos():
	today = nowdate()
	service_rows = frappe.get_all(
		"Tourism Service Order",
		filters={
			"status": ["in", ["Ordered", "In Progress"]],
			"service_date": ["<", today],
			"docstatus": ["<", 2],
		},
		fields=["name", "booking", "customer", "service_category", "service_date"],
		limit_page_length=300,
	)
	for row in service_rows:
		_create_todo(
			subject=f"[Tourism SLA] Service order overdue: {row.name} ({row.service_category}) from {row.service_date}.",
			reference_type="Tourism Service Order",
			reference_name=row.name,
		)

	stale_web = frappe.get_all(
		"Tourism Online Booking Request",
		filters={
			"status": ["in", ["New", "In Progress"]],
			"creation": ["<=", add_to_date(None, hours=-2)],
			"docstatus": ["<", 2],
		},
		fields=["name", "request_type", "customer_name", "creation"],
		limit_page_length=300,
	)
	for row in stale_web:
		_create_todo(
			subject=f"[Tourism SLA] Web request pending >2h: {row.name} ({row.request_type}).",
			reference_type="Tourism Online Booking Request",
			reference_name=row.name,
		)

