import frappe
from frappe import _
from frappe.model.document import Document


class TourismTravelPackage(Document):
	def validate(self):
		self.package_name = (self.package_name or "").strip()
		self.package_code = (self.package_code or "").strip().upper()
		self._validate_branch_company_match()
		self._validate_unique_code()

	def _validate_branch_company_match(self):
		if not self.branch or not self.company:
			return
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Validation"))

	def _validate_unique_code(self):
		existing = frappe.db.get_value(
			"Tourism Travel Package",
			{"company": self.company, "package_code": self.package_code},
			"name",
		)
		if existing and existing != self.name:
			frappe.throw(_("Package Code must be unique per company."), title=_("Duplicate"))

