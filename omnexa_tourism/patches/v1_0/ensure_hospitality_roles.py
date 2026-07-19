# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def execute():
	for name in ("Hotel Front Desk", "Hotel Housekeeping", "Hotel General Manager"):
		if frappe.db.exists("Role", name):
			continue
		frappe.get_doc(
			{"doctype": "Role", "desk_access": 1, "role_name": name}
		).insert(ignore_permissions=True)
