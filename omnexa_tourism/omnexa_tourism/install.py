# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def _ensure_hospitality_roles():
	for name in ("Hotel Front Desk", "Hotel Housekeeping", "Hotel General Manager"):
		if frappe.db.exists("Role", name):
			continue
		frappe.get_doc(
			{"doctype": "Role", "desk_access": 1, "role_name": name}
		).insert(ignore_permissions=True)


def after_install():
	_ensure_hospitality_roles()


def after_migrate():
	_ensure_hospitality_roles()

