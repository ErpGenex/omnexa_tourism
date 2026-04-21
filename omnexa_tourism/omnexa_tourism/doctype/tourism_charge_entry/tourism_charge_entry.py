import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_tourism.folio_ops import recalculate_guest_folio


class TourismChargeEntry(Document):
	def validate(self):
		self.amount = flt(self.quantity) * flt(self.rate)
		if not self.folio:
			frappe.throw(_("Guest folio is mandatory for charge entry."), title=_("Folio"))
		if flt(self.amount) <= 0:
			frappe.throw(_("Charge amount must be greater than zero."), title=_("Charge"))
		self._validate_folio_alignment()

	def on_update(self):
		recalculate_guest_folio(self.folio)

	def _validate_folio_alignment(self):
		if not self.folio:
			return
		folio = frappe.db.get_value(
			"Tourism Guest Folio",
			self.folio,
			["customer", "company", "branch", "hotel", "room_unit", "booking"],
			as_dict=True,
		)
		if not folio:
			frappe.throw(_("Guest folio does not exist."), title=_("Folio"))

		if folio.get("customer") != self.customer:
			frappe.throw(_("Charge entry customer must match the folio customer."), title=_("Validation"))
		if folio.get("company") != self.company or folio.get("branch") != self.branch:
			frappe.throw(_("Charge entry must belong to the same company and branch as the folio."), title=_("Validation"))
		if folio.get("hotel") and self.hotel and folio.get("hotel") != self.hotel:
			frappe.throw(_("Charge entry hotel must match the folio hotel."), title=_("Validation"))
		if folio.get("room_unit") and self.room_unit and folio.get("room_unit") != self.room_unit:
			frappe.throw(_("Charge entry room unit must match the folio room unit."), title=_("Validation"))
		if folio.get("booking") and self.booking and folio.get("booking") != self.booking:
			frappe.throw(_("Charge entry booking must match the folio booking."), title=_("Validation"))
