import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

from omnexa_tourism.tour_operator_ops import _ensure_folio_for_customer
from omnexa_tourism.folio_ops import ensure_charge_entry_for_service_order


class TourismActivityBooking(Document):
	def validate(self):
		self._validate_branch_company_match()

	def on_update(self):
		if self.status == "Billed":
			self._ensure_service_order_and_charge()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Validation"))

	def _ensure_service_order_and_charge(self):
		if self.service_order and frappe.db.exists("Tourism Service Order", self.service_order):
			return

		folio = _ensure_folio_for_customer(self.company, self.branch, self.customer)
		so = frappe.get_doc(
			{
				"doctype": "Tourism Service Order",
				"folio": folio,
				"booking": None,
				"customer": self.customer,
				"company": self.company,
				"branch": self.branch,
				"service_category": "Other",
				"source_app": "Tourism",
				"service_date": self.activity_date or nowdate(),
				"reference_doctype": "Tourism Activity Booking",
				"reference_name": self.name,
				"description": f"Activity: {self.activity_name}",
				"quantity": 1,
				"rate": self.price,
				"status": "Billed",
			}
		)
		so.insert(ignore_permissions=True)
		ensure_charge_entry_for_service_order(so)
		frappe.db.set_value(
			"Tourism Activity Booking",
			self.name,
			{"service_order": so.name, "charge_entry": so.charge_entry},
			update_modified=False,
		)

