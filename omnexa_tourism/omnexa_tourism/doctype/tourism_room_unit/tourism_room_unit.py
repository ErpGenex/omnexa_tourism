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
		self._validate_unique_unit_code()
		self._validate_status_transition()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

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
