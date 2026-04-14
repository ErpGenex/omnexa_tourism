import frappe
from frappe.tests.utils import FrappeTestCase


class TestTourismOperationModel(FrappeTestCase):
	def setUp(self):
		super().setUp()
		if not frappe.db.exists("Currency", "EGP"):
			frappe.get_doc(
				{"doctype": "Currency", "currency_name": "EGP", "symbol": "E£", "enabled": 1}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("Country", "Egypt"):
			frappe.get_doc(
				{"doctype": "Country", "country_name": "Egypt", "code": "EG"}
			).insert(ignore_permissions=True)

	def _make_company(self, label):
		abbr = f"TO{label}{frappe.generate_hash(length=2).upper()}"
		doc = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": f"Tourism Co {label}",
				"abbr": abbr,
				"default_currency": "EGP",
				"country": "Egypt",
				"status": "Active",
			}
		)
		doc.insert(ignore_permissions=True)
		return doc.name

	def _make_branch(self, company, code):
		doc = frappe.get_doc(
			{
				"doctype": "Branch",
				"company": company,
				"branch_name": f"Branch {code}",
				"branch_code": code,
				"status": "Active",
			}
		)
		doc.insert(ignore_permissions=True)
		return doc.name

	def test_operation_model_rejects_cross_company_branch(self):
		company_a = self._make_company("A")
		company_b = self._make_company("B")
		branch_b = self._make_branch(company_b, "BRB")
		doc = frappe.get_doc(
			{
				"doctype": "Tourism Operation Model",
				"model_name": "Hotel Ops",
				"company": company_a,
				"branch": branch_b,
				"operation_model": "Hotel",
				"status": "Active",
			}
		)
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_operation_model_inserts_with_same_company_branch(self):
		company = self._make_company("C")
		branch = self._make_branch(company, "BRC")
		doc = frappe.get_doc(
			{
				"doctype": "Tourism Operation Model",
				"model_name": "Resort Ops",
				"company": company,
				"branch": branch,
				"operation_model": "Resort",
				"status": "Active",
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Tourism Operation Model", doc.name))

	def test_room_unit_code_must_be_unique_in_branch(self):
		company = self._make_company("D")
		branch = self._make_branch(company, "BRD")
		frappe.get_doc(
			{
				"doctype": "Tourism Room Unit",
				"unit_name": "Room 101",
				"company": company,
				"branch": branch,
				"unit_code": "101",
				"capacity": 2,
				"status": "Available",
			}
		).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Tourism Room Unit",
					"unit_name": "Room 101 Dup",
					"company": company,
					"branch": branch,
					"unit_code": "101",
					"capacity": 2,
					"status": "Available",
				}
			).insert(ignore_permissions=True)

	def test_invalid_room_unit_status_transition_is_blocked(self):
		company = self._make_company("E")
		branch = self._make_branch(company, "BRE")
		unit = frappe.get_doc(
			{
				"doctype": "Tourism Room Unit",
				"unit_name": "Room 201",
				"company": company,
				"branch": branch,
				"unit_code": "201",
				"capacity": 2,
				"status": "Available",
			}
		).insert(ignore_permissions=True)
		unit.status = "Occupied"
		with self.assertRaises(frappe.ValidationError):
			unit.save(ignore_permissions=True)

	def test_disabled_unit_cannot_be_assigned_to_booking(self):
		company = self._make_company("F")
		branch = self._make_branch(company, "BRF")
		unit = frappe.get_doc(
			{
				"doctype": "Tourism Room Unit",
				"unit_name": "Room 301",
				"company": company,
				"branch": branch,
				"unit_code": "301",
				"capacity": 2,
				"status": "Disabled",
			}
		).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Tourism Booking",
					"guest_name": "Guest Test",
					"company": company,
					"branch": branch,
					"unit": unit.name,
					"check_in_date": "2026-04-20",
					"check_out_date": "2026-04-25",
					"status": "Draft",
				}
			).insert(ignore_permissions=True)
