# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TourismBooking(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_unit_assignment()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_unit_assignment(self):
		if not self.unit:
			return
		unit_data = frappe.db.get_value(
			"Tourism Room Unit",
			self.unit,
			["company", "branch", "status"],
			as_dict=True,
		)
		if not unit_data:
			frappe.throw(_("Selected unit does not exist."), title=_("Unit"))
		if unit_data.company != self.company or unit_data.branch != self.branch:
			frappe.throw(_("Selected unit must belong to the same company and branch."), title=_("Unit"))
		if unit_data.status == "Disabled":
			frappe.throw(_("Disabled unit cannot be assigned to a booking."), title=_("Unit"))
