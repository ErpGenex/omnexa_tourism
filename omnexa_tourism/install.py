# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

SUPPORTED_FRAPPE_MAJOR = 15


def enforce_supported_frappe_version():
	"""Fail fast when running on unsupported Frappe major versions."""
	version_text = (getattr(frappe, "__version__", "") or "").strip()
	if not version_text:
		return

	major_token = version_text.split(".", 1)[0]
	try:
		major = int(major_token)
	except ValueError:
		return

	if major != SUPPORTED_FRAPPE_MAJOR:
		frappe.throw(
			f"Unsupported Frappe version '{version_text}' for omnexa_tourism. "
			"Supported range is >=15.0,<16.0.",
			frappe.ValidationError,
		)


def _ensure_hospitality_roles():
	for name in ("Hotel Front Desk", "Hotel Housekeeping", "Hotel General Manager"):
		if frappe.db.exists("Role", name):
			continue
		frappe.get_doc({"doctype": "Role", "desk_access": 1, "role_name": name}).insert(
			ignore_permissions=True
		)


def after_install():
	_ensure_hospitality_roles()


def after_migrate():
	_ensure_hospitality_roles()

