import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from omnexa_tourism.tour_operator_ops import ensure_service_order_for_package_booking


class TourismPackageBooking(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_dates()

	def on_update(self):
		if self.status == "Billed":
			ensure_service_order_for_package_booking(self)

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Validation"))

	def _validate_dates(self):
		if self.start_date and self.end_date and getdate(self.end_date) < getdate(self.start_date):
			frappe.throw(_("End Date must be on or after Start Date."), title=_("Dates"))

