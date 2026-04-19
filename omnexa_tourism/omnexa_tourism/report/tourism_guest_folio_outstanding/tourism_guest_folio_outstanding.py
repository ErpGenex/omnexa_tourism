import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["company = %(company)s", "status != 'Cancelled'"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
	if filters.get("status"):
		conditions.append("status = %(status)s")
	if filters.get("from_date"):
		conditions.append("folio_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("folio_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			name AS guest_folio,
			folio_date,
			branch,
			customer,
			booking,
			status,
			total_charges,
			paid_amount,
			balance_due
		FROM `tabTourism Guest Folio`
		WHERE {' AND '.join(conditions)}
		ORDER BY balance_due DESC, folio_date DESC
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row.total_charges = flt(row.total_charges)
		row.paid_amount = flt(row.paid_amount)
		row.balance_due = flt(row.balance_due)
	return _columns(), data


def _columns():
	return [
		{"label": _("Guest Folio"), "fieldname": "guest_folio", "fieldtype": "Link", "options": "Tourism Guest Folio", "width": 150},
		{"label": _("Folio Date"), "fieldname": "folio_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": _("Booking"), "fieldname": "booking", "fieldtype": "Link", "options": "Tourism Booking", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Total Charges"), "fieldname": "total_charges", "fieldtype": "Currency", "width": 130},
		{"label": _("Paid Amount"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Balance Due"), "fieldname": "balance_due", "fieldtype": "Currency", "width": 120},
	]
