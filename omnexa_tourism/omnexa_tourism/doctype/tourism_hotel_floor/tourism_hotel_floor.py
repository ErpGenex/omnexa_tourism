import frappe
from frappe import _
from frappe.model.document import Document


class TourismHotelFloor(Document):
	def validate(self):
		self.floor_name = (self.floor_name or "").strip()
		self._validate_branch_company_match_from_hotel()

	def _validate_branch_company_match_from_hotel(self):
		if not self.hotel or not self.branch or not self.company:
			return
		hotel_data = frappe.db.get_value(
			"Tourism Hotel",
			self.hotel,
			["company", "branch"],
			as_dict=True,
		)
		if not hotel_data:
			frappe.throw(_("Hotel does not exist."), title=_("Hotel"))
		if hotel_data.get("company") != self.company or hotel_data.get("branch") != self.branch:
			frappe.throw(
				_("Hotel floor must belong to the same company and branch as the hotel."),
				title=_("Validation"),
			)

