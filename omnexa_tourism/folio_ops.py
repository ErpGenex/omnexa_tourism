import frappe
from frappe.utils import flt, nowdate


def ensure_guest_folio_for_booking(booking_doc):
	if getattr(booking_doc, "guest_folio", None) and frappe.db.exists(
		"Tourism Guest Folio", booking_doc.guest_folio
	):
		return booking_doc.guest_folio

	folio = frappe.get_doc(
		{
			"doctype": "Tourism Guest Folio",
			"booking": booking_doc.name,
			"customer": booking_doc.customer,
			"guest_name": booking_doc.guest_name,
			"company": booking_doc.company,
			"branch": booking_doc.branch,
			"hotel": getattr(booking_doc, "hotel", None),
			"room_unit": booking_doc.unit,
			"cost_center": getattr(booking_doc, "cost_center", None),
			"project": getattr(booking_doc, "project", None),
			"folio_date": nowdate(),
			"status": "Open",
		}
	)
	folio.insert(ignore_permissions=True)
	frappe.db.set_value(
		"Tourism Booking",
		booking_doc.name,
		"guest_folio",
		folio.name,
		update_modified=False,
	)
	return folio.name


def recalculate_guest_folio(folio_name: str):
	if not folio_name or not frappe.db.exists("Tourism Guest Folio", folio_name):
		return

	row = frappe.db.sql(
		"""
		SELECT
			COALESCE(SUM(amount), 0) AS total_charges
		FROM `tabTourism Charge Entry`
		WHERE folio = %s
			AND docstatus < 2
			AND status != 'Voided'
		""",
		(folio_name,),
		as_dict=True,
	)
	total_charges = flt(row[0].get("total_charges")) if row else 0.0
	paid_amount = 0.0
	balance_due = total_charges - paid_amount

	frappe.db.set_value(
		"Tourism Guest Folio",
		folio_name,
		{
			"total_charges": total_charges,
			"paid_amount": paid_amount,
			"balance_due": balance_due,
		},
		update_modified=False,
	)


def ensure_charge_entry_for_service_order(service_order_doc):
	if getattr(service_order_doc, "charge_entry", None) and frappe.db.exists(
		"Tourism Charge Entry", service_order_doc.charge_entry
	):
		return service_order_doc.charge_entry

	folio_name = getattr(service_order_doc, "folio", None)
	if not folio_name and getattr(service_order_doc, "booking", None):
		booking = frappe.get_doc("Tourism Booking", service_order_doc.booking)
		folio_name = ensure_guest_folio_for_booking(booking)

	charge = frappe.get_doc(
		{
			"doctype": "Tourism Charge Entry",
			"folio": folio_name,
			"booking": service_order_doc.booking,
			"service_order": service_order_doc.name,
			"customer": service_order_doc.customer,
			"company": service_order_doc.company,
			"branch": service_order_doc.branch,
			"hotel": getattr(service_order_doc, "hotel", None),
			"room_unit": getattr(service_order_doc, "room_unit", None),
			"charge_date": getattr(service_order_doc, "service_date", None) or nowdate(),
			"charge_type": getattr(service_order_doc, "service_category", None) or "Service",
			"reference_doctype": getattr(service_order_doc, "reference_doctype", None),
			"reference_name": getattr(service_order_doc, "reference_name", None),
			"description": service_order_doc.description,
			"quantity": service_order_doc.quantity,
			"rate": service_order_doc.rate,
			"amount": service_order_doc.amount,
			"cost_center": getattr(service_order_doc, "cost_center", None),
			"project": getattr(service_order_doc, "project", None),
			"status": "Billed",
		}
	)
	charge.insert(ignore_permissions=True)
	frappe.db.set_value(
		"Tourism Service Order",
		service_order_doc.name,
		"charge_entry",
		charge.name,
		update_modified=False,
	)
	recalculate_guest_folio(charge.folio)
	return charge.name
