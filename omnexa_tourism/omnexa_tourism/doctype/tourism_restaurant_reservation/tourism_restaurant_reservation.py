import frappe
from frappe import _
from frappe.model.document import Document


class TourismRestaurantReservation(Document):
	def validate(self):
		self._sync_name_from_venue()
		self._validate_slot_capacity()

	def on_update(self):
		# convenience: ensure a draft Restaurant Order exists for operations
		if self.restaurant_order and frappe.db.exists("Restaurant Order", self.restaurant_order):
			return
		if not frappe.db.exists("DocType", "Restaurant Order"):
			return
		order = frappe.get_doc(
			{
				"doctype": "Restaurant Order",
				"order_type": "Dine-in",
				"company": self.company,
				"branch": self.branch,
				"status": "Draft",
				"hold_order": 1,
			}
		)
		order.insert(ignore_permissions=True)
		frappe.db.set_value(
			"Tourism Restaurant Reservation",
			self.name,
			{"restaurant_order": order.name},
			update_modified=False,
		)

	def _sync_name_from_venue(self):
		if self.restaurant_venue and not self.restaurant_name:
			self.restaurant_name = frappe.db.get_value("Tourism Restaurant Venue", self.restaurant_venue, "venue_name")

	def _validate_slot_capacity(self):
		if self.status == "Cancelled" or not self.service_datetime:
			return
		capacity = 0
		if self.restaurant_venue:
			capacity = frappe.db.get_value("Tourism Restaurant Venue", self.restaurant_venue, "slot_capacity") or 0
		if not capacity:
			return
		used = frappe.db.count(
			"Tourism Restaurant Reservation",
			{
				"company": self.company,
				"branch": self.branch,
				"restaurant_venue": self.restaurant_venue,
				"service_datetime": self.service_datetime,
				"status": ["!=", "Cancelled"],
				"name": ["!=", self.name or ""],
			},
		)
		total = used + int(self.party_size or 0)
		if total > int(capacity):
			frappe.throw(
				_("Restaurant slot capacity exceeded. Capacity {0}, requested/used {1}.").format(capacity, total),
				title=_("Availability"),
			)

