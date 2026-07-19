import frappe
from frappe import _
from frappe.model.document import Document


class TourismBeachBooking(Document):
	def validate(self):
		self._sync_name_from_facility()
		self._validate_slot_capacity()

	def _sync_name_from_facility(self):
		if self.beach_facility and not self.beach_name:
			self.beach_name = frappe.db.get_value("Tourism Beach Facility", self.beach_facility, "facility_name")

	def _validate_slot_capacity(self):
		if self.status == "Cancelled" or not self.service_datetime:
			return
		capacity = 0
		if self.beach_facility:
			capacity = frappe.db.get_value("Tourism Beach Facility", self.beach_facility, "slot_capacity") or 0
		if not capacity:
			return
		used = frappe.db.count(
			"Tourism Beach Booking",
			{
				"company": self.company,
				"branch": self.branch,
				"beach_facility": self.beach_facility,
				"service_datetime": self.service_datetime,
				"status": ["!=", "Cancelled"],
				"name": ["!=", self.name or ""],
			},
		)
		total = used + int(self.party_size or 0)
		if total > int(capacity):
			frappe.throw(
				_("Beach slot capacity exceeded. Capacity {0}, requested/used {1}.").format(capacity, total),
				title=_("Availability"),
			)

