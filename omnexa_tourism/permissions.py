# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults


def enforce_branch_access_for_doc(doc, method=None):
	user = frappe.session.user
	if _tourism_user_can_access_all_branches(user):
		return
	branch = getattr(doc, "branch", None)
	company = getattr(doc, "company", None)
	if not branch:
		return
	allowed = set(_tourism_allowed_branches(user=user, company=company) or [])
	if branch not in allowed:
		frappe.throw("You are not allowed to access this hotel branch.", title="Branch Access")


def populate_company_branch_from_user_context(doc, method=None):
	apply_company_branch_defaults(doc)


def _tourism_user_can_access_all_branches(user=None):
	user = user or frappe.session.user
	if user in ("Administrator",):
		return True
	roles = set(frappe.get_roles(user))
	# Explicit policy: only General Manager (plus System Manager) can see all branches.
	return bool({"System Manager", "Hotel General Manager"} & roles)


def _tourism_allowed_branches(user=None, company=None):
	user = user or frappe.session.user
	if _tourism_user_can_access_all_branches(user):
		return None
	filters = {"user": user}
	if company:
		filters["company"] = company
	return frappe.get_all("User Branch Access", filters=filters, pluck="branch")


def _get_query_for_table(table: str, user=None):
	user = user or frappe.session.user
	allowed = _tourism_allowed_branches(user=user)
	if allowed is None:
		return ""
	if not allowed:
		return "1=0"
	quoted = ", ".join([frappe.db.escape(v) for v in allowed])
	return f"(`tab{table}`.branch in ({quoted}) or `tab{table}`.branch is null or `tab{table}`.branch = '')"


def tourism_booking_query_conditions(user=None):
	return _get_query_for_table("Tourism Booking", user)


def tourism_room_unit_query_conditions(user=None):
	return _get_query_for_table("Tourism Room Unit", user)


def tourism_room_type_query_conditions(user=None):
	return _get_query_for_table("Tourism Room Type", user)


def tourism_operation_model_query_conditions(user=None):
	return _get_query_for_table("Tourism Operation Model", user)


def tourism_hotel_query_conditions(user=None):
	return _get_query_for_table("Tourism Hotel", user)


def tourism_hotel_floor_query_conditions(user=None):
	return _get_query_for_table("Tourism Hotel Floor", user)


def tourism_guest_folio_query_conditions(user=None):
	return _get_query_for_table("Tourism Guest Folio", user)


def tourism_charge_entry_query_conditions(user=None):
	return _get_query_for_table("Tourism Charge Entry", user)


def tourism_service_order_query_conditions(user=None):
	return _get_query_for_table("Tourism Service Order", user)


def tourism_travel_vendor_query_conditions(user=None):
	return _get_query_for_table("Tourism Travel Vendor", user)


def tourism_travel_package_query_conditions(user=None):
	return _get_query_for_table("Tourism Travel Package", user)


def tourism_package_booking_query_conditions(user=None):
	return _get_query_for_table("Tourism Package Booking", user)


def tourism_transport_booking_query_conditions(user=None):
	return _get_query_for_table("Tourism Transport Booking", user)


def tourism_flight_booking_query_conditions(user=None):
	return _get_query_for_table("Tourism Flight Booking", user)


def tourism_activity_booking_query_conditions(user=None):
	return _get_query_for_table("Tourism Activity Booking", user)


def tourism_housekeeping_task_query_conditions(user=None):
	return _get_query_for_table("Tourism Housekeeping Task", user)


def tourism_vendor_contract_query_conditions(user=None):
	return _get_query_for_table("Tourism Vendor Contract", user)


def tourism_pricing_rule_query_conditions(user=None):
	return _get_query_for_table("Tourism Pricing Rule", user)


def tourism_online_booking_request_query_conditions(user=None):
	return _get_query_for_table("Tourism Online Booking Request", user)


def tourism_beach_booking_query_conditions(user=None):
	return _get_query_for_table("Tourism Beach Booking", user)


def tourism_restaurant_reservation_query_conditions(user=None):
	return _get_query_for_table("Tourism Restaurant Reservation", user)


def tourism_restaurant_venue_query_conditions(user=None):
	return _get_query_for_table("Tourism Restaurant Venue", user)


def tourism_beach_facility_query_conditions(user=None):
	return _get_query_for_table("Tourism Beach Facility", user)
