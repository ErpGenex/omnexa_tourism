import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_tourism.folio_ops import ensure_charge_entry_for_service_order, ensure_guest_folio_for_booking


class TourismServiceOrder(Document):
	def validate(self):
		self.amount = flt(self.quantity) * flt(self.rate)
		self._sync_from_booking()
		self._sync_reference_context()
		self._validate_booking_alignment()

	def on_update(self):
		if self.status == "Billed":
			ensure_charge_entry_for_service_order(self)

	def _sync_from_booking(self):
		if not self.booking:
			return
		booking = frappe.db.get_value(
			"Tourism Booking",
			self.booking,
			["customer", "company", "branch", "hotel", "unit", "guest_folio"],
			as_dict=True,
		)
		if not booking:
			frappe.throw(_("Booking does not exist."), title=_("Booking"))

		self.customer = booking.get("customer")
		self.company = booking.get("company")
		self.branch = booking.get("branch")
		self.hotel = booking.get("hotel")
		self.room_unit = booking.get("unit")

		if booking.get("guest_folio"):
			self.folio = booking.get("guest_folio")
		elif self.status in {"In Progress", "Completed", "Billed"}:
			booking_doc = frappe.get_doc("Tourism Booking", self.booking)
			self.folio = ensure_guest_folio_for_booking(booking_doc)

	def _validate_booking_alignment(self):
		if not self.booking:
			return
		if self.folio:
			folio = frappe.db.get_value(
				"Tourism Guest Folio",
				self.folio,
				["booking", "customer", "company", "branch"],
				as_dict=True,
			)
			if not folio:
				frappe.throw(_("Guest folio does not exist."), title=_("Folio"))
			if folio.get("booking") != self.booking:
				frappe.throw(_("Service order folio must belong to the same booking."), title=_("Validation"))
			if (
				folio.get("customer") != self.customer
				or folio.get("company") != self.company
				or folio.get("branch") != self.branch
			):
				frappe.throw(_("Service order must match the folio customer, company, and branch."), title=_("Validation"))

	def _sync_reference_context(self):
		if self.reference_doctype == "Restaurant Order" and self.reference_name:
			self.service_category = "Restaurant"
			self.source_app = "Restaurant"
		elif self.reference_doctype == "Service Ticket" and self.reference_name:
			self.source_app = "Services"
		elif not self.reference_doctype:
			self.source_app = self.source_app or "Tourism"
