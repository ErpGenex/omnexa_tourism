import frappe
from frappe import _
from frappe.model.document import Document


class TourismTravelVendor(Document):
	def validate(self):
		self.vendor_name = (self.vendor_name or "").strip()
		self._validate_branch_company_match()

	def _validate_branch_company_match(self):
		if not self.branch or not self.company:
			return
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Validation"))

