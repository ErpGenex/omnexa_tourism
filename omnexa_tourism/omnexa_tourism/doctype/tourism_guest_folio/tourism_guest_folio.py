import frappe
from frappe import _
from frappe.model.document import Document

from omnexa_tourism.folio_ops import recalculate_guest_folio


class TourismGuestFolio(Document):
	def validate(self):
		self._validate_booking_alignment()
		recalculate_guest_folio(self.name)

	def _validate_booking_alignment(self):
		if not self.booking:
			return
		booking = frappe.db.get_value(
			"Tourism Booking",
			self.booking,
			["customer", "company", "branch", "hotel", "unit"],
			as_dict=True,
		)
		if not booking:
			frappe.throw(_("Booking does not exist."), title=_("Booking"))
		if booking.get("customer") != self.customer:
			frappe.throw(_("Folio customer must match the booking customer."), title=_("Validation"))
		if booking.get("company") != self.company or booking.get("branch") != self.branch:
			frappe.throw(_("Folio must belong to the same company and branch as the booking."), title=_("Validation"))
		if booking.get("hotel") and self.hotel and booking.get("hotel") != self.hotel:
			frappe.throw(_("Folio hotel must match the booking hotel."), title=_("Validation"))
		if booking.get("unit") and self.room_unit and booking.get("unit") != self.room_unit:
			frappe.throw(_("Folio room unit must match the booking room unit."), title=_("Validation"))
