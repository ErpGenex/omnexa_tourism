import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate


def _ensure_folio_for_customer(company, branch, customer):
	# Create a standalone folio (not tied to a hotel booking) for tour operator charges.
	folio = frappe.get_doc(
		{
			"doctype": "Tourism Guest Folio",
			"booking": None,
			"customer": customer,
			"guest_name": None,
			"company": company,
			"branch": branch,
			"folio_date": nowdate(),
			"status": "Open",
		}
	)
	folio.insert(ignore_permissions=True)
	return folio.name


def ensure_service_order_for_package_booking(pkg_booking_doc):
	if getattr(pkg_booking_doc, "service_order", None) and frappe.db.exists(
		"Tourism Service Order", pkg_booking_doc.service_order
	):
		return pkg_booking_doc.service_order

	folio = _ensure_folio_for_customer(pkg_booking_doc.company, pkg_booking_doc.branch, pkg_booking_doc.customer)

	so = frappe.get_doc(
		{
			"doctype": "Tourism Service Order",
			"folio": folio,
			"booking": None,
			"customer": pkg_booking_doc.customer,
			"company": pkg_booking_doc.company,
			"branch": pkg_booking_doc.branch,
			"service_category": "Other",
			"source_app": "Tourism",
			"service_date": pkg_booking_doc.start_date or nowdate(),
			"reference_doctype": "Tourism Package Booking",
			"reference_name": pkg_booking_doc.name,
			"description": f"Travel package booking {pkg_booking_doc.travel_package}",
			"quantity": 1,
			"rate": flt(pkg_booking_doc.package_price),
			"status": "Billed",
		}
	)
	so.insert(ignore_permissions=True)

	frappe.db.set_value(
		"Tourism Package Booking",
		pkg_booking_doc.name,
		{
			"folio": folio,
			"service_order": so.name,
			"charge_entry": so.charge_entry,
		},
		update_modified=False,
	)
	return so.name

