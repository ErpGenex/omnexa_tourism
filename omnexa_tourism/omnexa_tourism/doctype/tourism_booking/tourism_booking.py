# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate

from omnexa_tourism.folio_ops import ensure_guest_folio_for_booking


ALLOWED_BOOKING_STATUS = {
	"Draft": {"Confirmed", "Cancelled"},
	"Confirmed": {"Checked In", "Cancelled"},
	"Checked In": {"Checked Out", "Cancelled"},
	"Checked Out": set(),
	"Cancelled": set(),
}


class TourismBooking(Document):
	def validate(self):
		self._validate_dates_and_nights()
		self._validate_branch_company_match()
		self._validate_customer_company()
		self._validate_unit_assignment()
		self._validate_no_overlapping_booking()
		self._validate_status_transition()
		self._validate_lifecycle_controls()
		self._set_charges()

	def before_save(self):
		if not self.is_new():
			self._previous_status = frappe.db.get_value("Tourism Booking", self.name, "status")
		else:
			self._previous_status = None

	def on_update(self):
		prev = getattr(self, "_previous_status", None)
		if self.status == "Checked In" and prev != "Checked In":
			self._ensure_guest_folio()
		if self.status == "Checked Out" and prev != "Checked Out":
			self._on_checked_out()

	def _validate_dates_and_nights(self):
		if not self.check_in_date or not self.check_out_date:
			return
		if getdate(self.check_out_date) <= getdate(self.check_in_date):
			frappe.throw(_("Check-out date must be after check-in date."), title=_("Dates"))
		self.nights = date_diff(self.check_out_date, self.check_in_date)
		if self.nights < 1:
			self.nights = 1

	def _set_charges(self):
		n = flt(self.nights) or 1
		self.total_room_charges = flt(self.rate_per_night) * n

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_customer_company(self):
		if not self.customer:
			return
		cc = frappe.db.get_value("Customer", self.customer, "company")
		if cc and cc != self.company:
			frappe.throw(_("Customer belongs to a different company."), title=_("Customer"))

	def _validate_unit_assignment(self):
		if not self.unit:
			return
		unit_data = frappe.db.get_value(
			"Tourism Room Unit",
			self.unit,
			["company", "branch", "hotel", "status"],
			as_dict=True,
		)
		if not unit_data:
			frappe.throw(_("Selected unit does not exist."), title=_("Unit"))
		if unit_data.company != self.company or unit_data.branch != self.branch:
			frappe.throw(_("Selected unit must belong to the same company and branch."), title=_("Unit"))
		if hasattr(self, "hotel"):
			unit_hotel = unit_data.get("hotel")
			if unit_hotel:
				if not getattr(self, "hotel", None):
					self.hotel = unit_hotel
				elif self.hotel != unit_hotel:
					frappe.throw(_("Selected room unit belongs to a different hotel."), title=_("Hotel"))
		if unit_data.status == "Disabled":
			frappe.throw(_("Disabled unit cannot be assigned to a booking."), title=_("Unit"))

	def _validate_no_overlapping_booking(self):
		if not self.unit or not self.check_in_date or not self.check_out_date:
			return
		if self.status == "Cancelled":
			return
		# Half-open [check_in, check_out): overlap iff start < other_end and other_start < end
		filters = [
			["unit", "=", self.unit],
			["status", "!=", "Cancelled"],
			["check_in_date", "<", self.check_out_date],
			["check_out_date", ">", self.check_in_date],
		]
		candidates = frappe.get_all("Tourism Booking", filters=filters, pluck="name")
		for name in candidates:
			if self.is_new() or name != self.name:
				frappe.throw(
					_("Room unit already has a booking overlapping these dates ({0}).").format(name),
					title=_("Availability"),
				)

	def _validate_status_transition(self):
		if self.is_new():
			return
		previous_status = frappe.db.get_value("Tourism Booking", self.name, "status")
		if not previous_status or previous_status == self.status:
			return
		allowed_next = ALLOWED_BOOKING_STATUS.get(previous_status, set())
		if self.status not in allowed_next:
			frappe.throw(
				_("Invalid booking status transition from {0} to {1}.").format(
					previous_status, self.status
				),
				title=_("Status"),
			)

	def _validate_lifecycle_controls(self):
		if self.status in {"Confirmed", "Checked In", "Checked Out"}:
			if not self.customer:
				frappe.throw(_("Customer is mandatory for confirmed/active bookings."), title=_("Booking"))
			if not self.unit:
				frappe.throw(_("Room unit is mandatory for confirmed/active bookings."), title=_("Booking"))
			if flt(self.rate_per_night) <= 0:
				frappe.throw(_("Rate per night must be greater than zero."), title=_("Pricing"))

	def _on_checked_out(self):
		self._ensure_guest_folio()
		self._ensure_housekeeping_task()
		if self._can_create_sales_invoice():
			self._ensure_sales_invoice()

	def _ensure_guest_folio(self):
		ensure_guest_folio_for_booking(self)

	def _can_create_sales_invoice(self):
		return (
			"omnexa_accounting" in frappe.get_installed_apps()
			and frappe.db.exists("DocType", "Sales Invoice")
			and not self.sales_invoice
		)

	def _ensure_housekeeping_task(self):
		if self.housekeeping_task and frappe.db.exists("Tourism Housekeeping Task", self.housekeeping_task):
			return
		hk = frappe.get_doc(
			{
				"doctype": "Tourism Housekeeping Task",
				"company": self.company,
				"branch": self.branch,
				"unit": self.unit,
				"booking": self.name,
				"task_type": "Post-stay clean",
				"status": "Pending",
				"priority": "Normal",
				"scheduled_date": self.check_out_date,
			}
		)
		hk.insert(ignore_permissions=True)
		frappe.db.set_value(
			"Tourism Booking",
			self.name,
			"housekeeping_task",
			hk.name,
			update_modified=False,
		)

	def _ensure_sales_invoice(self):
		try:
			currency = frappe.db.get_value("Company", self.company, "default_currency")
			if not currency:
				frappe.log_error("Tourism Booking: company has no default currency", "Tourism Sales Invoice")
				return
			si = frappe.new_doc("Sales Invoice")
			si.company = self.company
			si.branch = self.branch
			si.customer = self.customer
			si.posting_date = self.check_out_date
			si.currency = currency
			si.conversion_rate = 1.0
			nights = int(self.nights or 1)
			si.append(
				"items",
				{
					"item_code": "ROOM-STAY",
					"qty": float(nights),
					"rate": flt(self.rate_per_night),
				},
			)
			si.insert(ignore_permissions=True)
			si.submit()
			frappe.db.set_value(
				"Tourism Booking",
				self.name,
				"sales_invoice",
				si.name,
				update_modified=False,
			)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Tourism Booking Sales Invoice")
