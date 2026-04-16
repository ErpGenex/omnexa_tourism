import frappe
from frappe import _
from frappe.model.document import Document


class TourismHotel(Document):
	def validate(self):
		self.hotel_name = (self.hotel_name or "").strip()
		self._validate_branch_company_match()

	def _validate_branch_company_match(self):
		if not self.branch or not self.company:
			return
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Validation"))

