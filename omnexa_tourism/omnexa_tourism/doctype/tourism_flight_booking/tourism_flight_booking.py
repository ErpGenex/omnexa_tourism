import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from omnexa_tourism.tour_operator_ops import _ensure_folio_for_customer
from omnexa_tourism.folio_ops import ensure_charge_entry_for_service_order


class TourismFlightBooking(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_workflow_rules()
		self._sync_pricing_totals()

	def on_update(self):
		self._sync_status_dates()
		if self.status == "Billed":
			self._ensure_service_order_and_charge()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Validation"))

	def _validate_workflow_rules(self):
		if self.trip_type == "Round-trip" and not self.return_datetime:
			frappe.throw(_("Return date/time is required for Round-trip."), title=_("Validation"))

		if self.status in ("Ticketed", "Billed") and not self.ticket_no:
			frappe.throw(_("Ticket Number is required when status is Ticketed or Billed."), title=_("Validation"))

	def _sync_pricing_totals(self):
		self.total_price = (self.base_fare or 0) + (self.taxes or 0) + (self.fees or 0)
		self.markup_amount = _calculate_markup_amount(
			total_price=self.total_price, markup_type=self.markup_type, markup_value=self.markup_value
		)
		if self.auto_price or not self.price:
			self.price = self.total_price + (self.markup_amount or 0)

	def _sync_status_dates(self):
		# These are informational timestamps to support ticketing workflow
		if self.status == "Confirmed" and not self.confirmed_on:
			self.confirmed_on = frappe.utils.now()
		if self.status == "Ticketed" and not self.ticketed_on:
			self.ticketed_on = frappe.utils.now()

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
				"service_date": (getdate(self.departure_datetime) if self.departure_datetime else getdate(nowdate())),
				"reference_doctype": "Tourism Flight Booking",
				"reference_name": self.name,
				"description": f"Flight: {self.from_airport} → {self.to_airport} ({self.trip_type}, {self.cabin_class}) (PNR: {self.pnr or '-'})",
				"quantity": 1,
				"rate": self.price,
				"status": "Billed",
			}
		)
		so.insert(ignore_permissions=True)
		ensure_charge_entry_for_service_order(so)
		frappe.db.set_value(
			"Tourism Flight Booking",
			self.name,
			{"service_order": so.name, "charge_entry": so.charge_entry},
			update_modified=False,
		)


@frappe.whitelist()
def suggest_fare_rule(vendor, from_airport, to_airport, trip_type="One-way", cabin_class="Economy", posting_date=None):
	"""
	Return the best matching active fare rule from active contracts.
	This is a pricing helper for ticket booking, not airline operations.
	"""
	posting_date = getdate(posting_date) if posting_date else getdate(nowdate())
	rows = frappe.db.sql(
		"""
		SELECT
			r.fare_basis, r.base_fare, r.taxes, r.fees, COALESCE(r.currency, c.currency) AS currency,
			c.name AS contract
		FROM `tabTourism Vendor Contract` c
		INNER JOIN `tabTourism Vendor Fare Rule` r ON r.parent = c.name
		WHERE
			c.status = 'Active'
			AND c.vendor = %(vendor)s
			AND c.valid_from <= %(posting_date)s
			AND (c.valid_until IS NULL OR c.valid_until >= %(posting_date)s)
			AND r.is_active = 1
			AND r.from_airport = %(from_airport)s
			AND r.to_airport = %(to_airport)s
			AND r.trip_type = %(trip_type)s
			AND r.cabin_class = %(cabin_class)s
		ORDER BY c.modified DESC, r.idx ASC
		LIMIT 1
		""",
		{
			"vendor": vendor,
			"from_airport": from_airport,
			"to_airport": to_airport,
			"trip_type": trip_type,
			"cabin_class": cabin_class,
			"posting_date": posting_date,
		},
		as_dict=True,
	)
	return rows[0] if rows else {}


def _calculate_markup_amount(total_price, markup_type, markup_value):
	total_price = total_price or 0
	markup_value = markup_value or 0
	markup_type = (markup_type or "Percent").strip()
	if markup_value == 0:
		return 0
	if markup_type == "Amount":
		return float(markup_value)
	# Percent
	return float(total_price) * float(markup_value) / 100.0


@frappe.whitelist()
def suggest_pricing(company, branch, customer, vendor, from_airport, to_airport, trip_type="One-way", cabin_class="Economy", posting_date=None):
	posting_date = getdate(posting_date) if posting_date else getdate(nowdate())
	fare = suggest_fare_rule(
		vendor=vendor,
		from_airport=from_airport,
		to_airport=to_airport,
		trip_type=trip_type,
		cabin_class=cabin_class,
		posting_date=posting_date,
	)
	markup = _suggest_markup_rule(
		company=company,
		branch=branch,
		customer=customer,
		vendor=vendor,
		from_airport=from_airport,
		to_airport=to_airport,
		trip_type=trip_type,
		cabin_class=cabin_class,
	)

	total_price = float((fare.get("base_fare") or 0) + (fare.get("taxes") or 0) + (fare.get("fees") or 0))
	markup_amount = _calculate_markup_amount(
		total_price=total_price,
		markup_type=markup.get("markup_type") or "Percent",
		markup_value=markup.get("markup_value") or 0,
	)
	return {
		"fare": fare,
		"markup": markup,
		"computed": {"total_price": total_price, "markup_amount": markup_amount, "billed_price": total_price + markup_amount},
	}


def _suggest_markup_rule(company, branch, customer, vendor, from_airport, to_airport, trip_type, cabin_class):
	"""
	Pick the best matching Tourism Pricing Rule.
	Scoring rules:
	- Only active rules, applies_to='Flight Ticket'
	- Match company + branch exactly
	- Optional dimensions can be blank or exact match
	- Lower priority wins, then more specific wins
	"""
	filters = {
		"is_active": 1,
		"applies_to": "Flight Ticket",
		"company": company,
		"branch": branch,
	}
	candidates = frappe.get_all(
		"Tourism Pricing Rule",
		filters=filters,
		fields=[
			"name",
			"customer",
			"vendor",
			"from_airport",
			"to_airport",
			"trip_type",
			"cabin_class",
			"priority",
			"markup_type",
			"markup_value",
		],
		order_by="priority asc, modified desc",
		limit_page_length=200,
	)

	def _match_or_blank(rule_value, actual_value):
		return (not rule_value) or (rule_value == actual_value)

	best = None
	best_score = None
	for r in candidates:
		if not _match_or_blank(r.get("customer"), customer):
			continue
		if not _match_or_blank(r.get("vendor"), vendor):
			continue
		if not _match_or_blank(r.get("from_airport"), from_airport):
			continue
		if not _match_or_blank(r.get("to_airport"), to_airport):
			continue
		if not _match_or_blank(r.get("trip_type"), trip_type):
			continue
		if not _match_or_blank(r.get("cabin_class"), cabin_class):
			continue

		specificity = sum(1 for k in ("customer", "vendor", "from_airport", "to_airport", "trip_type", "cabin_class") if r.get(k))
		# Lower priority is better; higher specificity is better
		score = (int(r.get("priority") or 100), -specificity)
		if best_score is None or score < best_score:
			best = r
			best_score = score

	return best or {}

