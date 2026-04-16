import frappe
from frappe.model.document import Document


class TourismVendorContract(Document):
	def validate(self):
		self._validate_dates()

	def _validate_dates(self):
		if self.valid_until and self.valid_from and self.valid_until < self.valid_from:
			frappe.throw("Valid Until must be on or after Valid From.")

