# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document

ALLOWED_STATUS_TRANSITIONS = {
	"Available": {"Reserved", "Maintenance", "Disabled"},
	"Reserved": {"Occupied", "Available", "Maintenance", "Disabled"},
	"Occupied": {"Available", "Maintenance", "Disabled"},
	"Maintenance": {"Available", "Disabled"},
	"Disabled": {"Available"},
}


class TourismRoomUnit(Document):
	def validate(self):
		self.unit_code = (self.unit_code or "").strip().upper()
		self._validate_branch_company_match()
		self._validate_hotel_branch_company_match()
		self._validate_floor_hotel_match()
		self._validate_room_type_branch()
		self._validate_unique_unit_code()
		self._validate_status_transition()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_room_type_branch(self):
		room_type = getattr(self, "room_type", None)
		if not room_type:
			return
		rt = frappe.db.get_value(
			"Tourism Room Type", room_type, ["company", "branch"], as_dict=True
		)
		if not rt:
			frappe.throw(_("Room Type does not exist."), title=_("Room Type"))
		if rt.company != self.company or rt.branch != self.branch:
			frappe.throw(_("Room Type must belong to the same company and branch."), title=_("Room Type"))

	def _validate_hotel_branch_company_match(self):
		if not getattr(self, "hotel", None):
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
				_("Hotel must belong to the same company and branch."),
				title=_("Hotel"),
			)

	def _validate_floor_hotel_match(self):
		if not getattr(self, "hotel_floor", None):
			return

		floor_data = frappe.db.get_value(
			"Tourism Hotel Floor",
			self.hotel_floor,
			["hotel", "company", "branch"],
			as_dict=True,
		)
		if not floor_data:
			frappe.throw(_("Hotel floor does not exist."), title=_("Floor"))

		# If hotel isn't set yet, infer it from the selected floor.
		if not getattr(self, "hotel", None):
			self.hotel = floor_data.get("hotel")

		if floor_data.get("company") != self.company or floor_data.get("branch") != self.branch:
			frappe.throw(
				_("Hotel floor must belong to the same company and branch."),
				title=_("Floor"),
			)

		if getattr(self, "hotel", None) and floor_data.get("hotel") != self.hotel:
			frappe.throw(
				_("Selected floor does not belong to the selected hotel."),
				title=_("Validation"),
			)

	def _validate_unique_unit_code(self):
		dupe = frappe.db.exists(
			"Tourism Room Unit",
			{"company": self.company, "branch": self.branch, "unit_code": self.unit_code},
		)
		if dupe and (self.is_new() or dupe != self.name):
			frappe.throw(
				_("Unit Code must be unique within the same company and branch."),
				title=_("Validation"),
			)

	def _validate_status_transition(self):
		if self.is_new():
			return
		previous_status = frappe.db.get_value("Tourism Room Unit", self.name, "status")
		if not previous_status or previous_status == self.status:
			return
		allowed_next = ALLOWED_STATUS_TRANSITIONS.get(previous_status, set())
		if self.status not in allowed_next:
			frappe.throw(
				_("Invalid unit status transition from {0} to {1}.").format(
					previous_status, self.status
				),
				title=_("Validation"),
			)
