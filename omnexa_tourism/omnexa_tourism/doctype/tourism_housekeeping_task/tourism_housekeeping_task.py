# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TourismHousekeepingTask(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_unit_branch()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_unit_branch(self):
		if not self.unit:
			return
		u = frappe.db.get_value(
			"Tourism Room Unit", self.unit, ["company", "branch"], as_dict=True
		)
		if not u:
			frappe.throw(_("Room unit does not exist."), title=_("Unit"))
		if u.company != self.company or u.branch != self.branch:
			frappe.throw(_("Room unit must belong to the same company and branch."), title=_("Unit"))
