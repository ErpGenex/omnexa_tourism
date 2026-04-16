import frappe
from frappe.utils import flt


def post_charge_entry_journal(doc, method=None):
	if not doc or not getattr(doc, "name", None):
		return

	if doc.status == "Billed":
		_create_charge_journal_if_needed(doc)
	elif doc.status == "Voided":
		_reverse_charge_journal_if_any(doc)


def _create_charge_journal_if_needed(doc):
	if getattr(doc, "journal_entry", None):
		return
	if not flt(doc.amount):
		return
	if "Journal Entry" not in frappe.get_all("DocType", pluck="name"):
		return

	hotel = _get_hotel_accounts(doc)
	if not hotel:
		return

	receivable_account = hotel.get("receivable_account")
	revenue_account = hotel.get("revenue_account")
	if not receivable_account or not revenue_account:
		return

	je = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": doc.company,
			"posting_date": doc.charge_date,
			"user_remark": f"Tourism charge posting for {doc.name}",
			"accounts": [
				{
					"account": receivable_account,
					"party_type": "Customer",
					"party": doc.customer,
					"debit_in_account_currency": flt(doc.amount),
					"cost_center": doc.cost_center,
					"project": doc.project,
				},
				{
					"account": revenue_account,
					"credit_in_account_currency": flt(doc.amount),
					"cost_center": doc.cost_center,
					"project": doc.project,
				},
			],
		}
	)
	je.insert(ignore_permissions=True)
	je.submit()
	frappe.db.set_value(
		"Tourism Charge Entry",
		doc.name,
		"journal_entry",
		je.name,
		update_modified=False,
	)


def _reverse_charge_journal_if_any(doc):
	je_name = getattr(doc, "journal_entry", None)
	if not je_name or not frappe.db.exists("Journal Entry", je_name):
		return

	je = frappe.get_doc("Journal Entry", je_name)
	if je.docstatus == 1:
		je.cancel()


def _get_hotel_accounts(doc):
	hotel = getattr(doc, "hotel", None)
	if not hotel:
		hotel = frappe.db.get_value("Tourism Guest Folio", doc.folio, "hotel")
	if not hotel:
		return None
	return frappe.db.get_value(
		"Tourism Hotel",
		hotel,
		["revenue_account", "receivable_account"],
		as_dict=True,
	)
