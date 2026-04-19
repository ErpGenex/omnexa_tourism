# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Ensure Tourism script reports are visible on the desk for operations, finance, and sales roles."""

import frappe

REPORT_NAMES = (
	"Tourism Daily Revenue",
	"Tourism Occupancy",
	"Tourism Booking Status Summary",
	"Tourism Channel Performance",
	"Tourism KPI Summary",
	"Tourism Room Type Performance",
	"Tourism Lead Time Analysis",
	"Tourism Cancellation & No-show",
	"Tourism Service Profitability",
	"Tourism Package Profitability",
	"Tourism Flight Ticket Sales",
	"Tourism Housekeeping Performance",
	"Tourism Guest Folio Outstanding",
)

ROLES = (
	"System Manager",
	"Company Admin",
	"Hotel General Manager",
	"Hotel Front Desk",
	"Hotel Housekeeping",
	"Desk User",
	"Report Manager",
	"Accounts Manager",
	"Accounts User",
	"Sales Manager",
	"Sales User",
)


def execute():
	valid_roles = set(frappe.get_all("Role", pluck="name"))
	roles = tuple(r for r in ROLES if r in valid_roles)
	if not roles:
		return

	for name in REPORT_NAMES:
		if not frappe.db.exists("Report", name):
			continue
		doc = frappe.get_doc("Report", name)
		doc.roles = []
		for role in roles:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)

	frappe.clear_cache()
