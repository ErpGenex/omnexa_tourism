import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class TourismOnlineBookingRequest(Document):
	def validate(self):
		self._validate_basic()

	def _validate_basic(self):
		if self.request_type == "Hotel":
			if not self.room_unit or not self.check_in_date or not self.check_out_date:
				frappe.throw(_("Hotel request requires Room Unit, Check In and Check Out."), title=_("Validation"))
			if not _is_room_available(self.room_unit, self.check_in_date, self.check_out_date, exclude_booking=None):
				frappe.throw(_("Selected room is not available for the requested dates."), title=_("Availability"))
		if self.request_type == "Flight Ticket":
			if not self.from_airport or not self.to_airport or not self.departure_datetime:
				frappe.throw(_("Flight request requires From, To and Departure."), title=_("Validation"))
			if self.trip_type == "Round-trip" and not self.return_datetime:
				frappe.throw(_("Return is required for Round-trip."), title=_("Validation"))
		if self.request_type in ("Beach", "Restaurant") and not self.service_datetime:
			frappe.throw(_("Service Date/Time is required for Beach and Restaurant requests."), title=_("Validation"))
		if self.request_type == "Activity":
			if not self.activity_name or not (self.activity_date or self.service_datetime):
				frappe.throw(_("Activity request requires Activity Name and Activity Date."), title=_("Validation"))

	@frappe.whitelist()
	def convert_to_operational_docs(self):
		"""
		Convert an online request into operational docs.
		We keep it intentionally minimal (requests may need staff verification).
		"""
		self.check_permission("write")
		if self.status in ("Converted", "Closed", "Cancelled"):
			frappe.throw(_("Request is already processed."), title=_("Validation"))

		if self.request_type == "Hotel":
			booking = frappe.get_doc(
				{
					"doctype": "Tourism Booking",
					"customer": _ensure_customer_for_request(self),
					"company": self.company,
					"branch": self.branch,
					"unit": self.room_unit,
					"check_in_date": getdate(self.check_in_date),
					"check_out_date": getdate(self.check_out_date),
					"adults": 1,
					"children": 0,
					"rate_per_night": 0,
					"booking_channel": "Other",
					"status": "Draft",
				}
			)
			booking.insert(ignore_permissions=True)
			self.created_booking = booking.name

		elif self.request_type == "Flight Ticket":
			fb = frappe.get_doc(
				{
					"doctype": "Tourism Flight Booking",
					"customer": _ensure_customer_for_request(self),
					"company": self.company,
					"branch": self.branch,
					"vendor": None,
					"from_airport": self.from_airport,
					"to_airport": self.to_airport,
					"departure_datetime": self.departure_datetime,
					"return_datetime": self.return_datetime,
					"trip_type": self.trip_type or "One-way",
					"cabin_class": self.cabin_class or "Economy",
					"passengers": self.passengers or 1,
					"currency": None,
					"base_fare": 0,
					"taxes": 0,
					"fees": 0,
					"auto_price": 1,
					"markup_type": "Percent",
					"markup_value": 0,
					"price": 0,
					"status": "Draft",
				}
			)
			fb.insert(ignore_permissions=True)
			self.created_flight_booking = fb.name

		elif self.request_type == "Beach":
			beach = frappe.get_doc(
				{
					"doctype": "Tourism Beach Booking",
					"customer": _ensure_customer_for_request(self),
					"company": self.company,
					"branch": self.branch,
					"hotel": self.hotel,
					"beach_facility": self.beach_facility,
					"beach_name": self.location or "Beach",
					"service_datetime": self.service_datetime,
					"party_size": self.party_size or 2,
					"status": "Draft",
					"online_request": self.name,
				}
			)
			beach.insert(ignore_permissions=True)
			self.created_beach_booking = beach.name

		elif self.request_type == "Restaurant":
			res = frappe.get_doc(
				{
					"doctype": "Tourism Restaurant Reservation",
					"customer": _ensure_customer_for_request(self),
					"company": self.company,
					"branch": self.branch,
					"hotel": self.hotel,
					"restaurant_venue": self.restaurant_venue,
					"restaurant_name": self.location or "Restaurant",
					"service_datetime": self.service_datetime,
					"party_size": self.party_size or 2,
					"status": "Draft",
					"online_request": self.name,
				}
			)
			res.insert(ignore_permissions=True)
			# reservation on_update may create a draft Restaurant Order
			self.created_restaurant_order = res.restaurant_order

		elif self.request_type == "Activity":
			ab = frappe.get_doc(
				{
					"doctype": "Tourism Activity Booking",
					"customer": _ensure_customer_for_request(self),
					"company": self.company,
					"branch": self.branch,
					"vendor": None,
					"activity_name": self.activity_name,
					"location": self.location,
					"activity_date": getdate(self.activity_date) if self.activity_date else getdate(self.service_datetime),
					"participants": self.participants or 1,
					"currency": None,
					"price": 0,
					"status": "Draft",
				}
			)
			ab.insert(ignore_permissions=True)
			self.created_activity_booking = ab.name

		self.status = "Converted"
		self.save(ignore_permissions=True)
		return {
			"created_booking": self.created_booking,
			"created_flight_booking": self.created_flight_booking,
			"created_beach_booking": getattr(self, "created_beach_booking", None),
			"created_restaurant_order": self.created_restaurant_order,
			"created_activity_booking": self.created_activity_booking,
		}


@frappe.whitelist(allow_guest=True)
def submit_online_request(payload: dict):
	"""
	Guest-safe endpoint to submit an online request.
	Returns request name for tracking.
	"""
	if not payload:
		frappe.throw(_("Missing payload."))

	for k in ("request_type", "customer_name", "email", "company", "branch"):
		if not payload.get(k):
			frappe.throw(_("Missing field: {0}").format(k))

	doc = frappe.get_doc(
		{
			"doctype": "Tourism Online Booking Request",
			"request_type": payload.get("request_type"),
			"customer_name": payload.get("customer_name"),
			"email": payload.get("email"),
			"phone": payload.get("phone"),
			"company": payload.get("company"),
			"branch": payload.get("branch"),
			"hotel": payload.get("hotel"),
			"room_unit": payload.get("room_unit"),
			"restaurant_venue": payload.get("restaurant_venue"),
			"beach_facility": payload.get("beach_facility"),
			"check_in_date": payload.get("check_in_date"),
			"check_out_date": payload.get("check_out_date"),
			"from_airport": payload.get("from_airport"),
			"to_airport": payload.get("to_airport"),
			"departure_datetime": payload.get("departure_datetime"),
			"return_datetime": payload.get("return_datetime"),
			"trip_type": payload.get("trip_type") or "One-way",
			"cabin_class": payload.get("cabin_class") or "Economy",
			"passengers": payload.get("passengers") or 1,
			"service_datetime": payload.get("service_datetime"),
			"party_size": payload.get("party_size") or 2,
			"activity_name": payload.get("activity_name"),
			"location": payload.get("location"),
			"activity_date": payload.get("activity_date"),
			"participants": payload.get("participants") or 1,
			"notes": payload.get("notes"),
			"source": payload.get("source") or "Website",
			"status": "New",
		}
	)
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "status": doc.status, "submitted_on": nowdate()}


@frappe.whitelist(allow_guest=True)
def get_online_booking_options(company=None, branch=None, check_in_date=None, check_out_date=None):
	hotels = frappe.get_all(
		"Tourism Hotel",
		filters=_optional_filters({"company": company, "branch": branch}),
		fields=["name", "hotel_name"],
		order_by="hotel_name asc",
		limit_page_length=200,
	)
	restaurants = frappe.get_all(
		"Tourism Restaurant Venue",
		filters=_optional_filters({"company": company, "branch": branch, "is_active": 1}),
		fields=["name", "venue_name", "slot_capacity"],
		order_by="venue_name asc",
		limit_page_length=200,
	)
	beaches = frappe.get_all(
		"Tourism Beach Facility",
		filters=_optional_filters({"company": company, "branch": branch, "is_active": 1}),
		fields=["name", "facility_name", "slot_capacity"],
		order_by="facility_name asc",
		limit_page_length=200,
	)
	rooms = get_available_room_units(company, branch, check_in_date, check_out_date)
	return {"hotels": hotels, "rooms": rooms, "restaurants": restaurants, "beaches": beaches}


@frappe.whitelist(allow_guest=True)
def get_available_room_units(company=None, branch=None, check_in_date=None, check_out_date=None):
	filters = _optional_filters({"company": company, "branch": branch, "status": ["!=", "Disabled"]})
	units = frappe.get_all(
		"Tourism Room Unit",
		filters=filters,
		fields=["name", "unit_name", "hotel", "capacity"],
		order_by="unit_name asc",
		limit_page_length=500,
	)
	if not check_in_date or not check_out_date:
		return units
	available = []
	for u in units:
		if _is_room_available(u.name, check_in_date, check_out_date, exclude_booking=None):
			available.append(u)
	return available


@frappe.whitelist(allow_guest=True)
def get_slot_usage(company, branch, doctype_name, resource_name, service_datetime):
	"""
	Check slot utilization for restaurant/beach resources.
	doctype_name: Tourism Restaurant Reservation | Tourism Beach Booking
	"""
	if doctype_name not in ("Tourism Restaurant Reservation", "Tourism Beach Booking"):
		frappe.throw(_("Invalid doctype for slot usage."))
	link_field = "restaurant_venue" if doctype_name == "Tourism Restaurant Reservation" else "beach_facility"
	capacity_doctype = "Tourism Restaurant Venue" if doctype_name == "Tourism Restaurant Reservation" else "Tourism Beach Facility"
	capacity_field = "slot_capacity"
	capacity = frappe.db.get_value(capacity_doctype, resource_name, capacity_field) or 0
	used = frappe.db.sql(
		f"""
		SELECT COALESCE(SUM(party_size), 0)
		FROM `tab{doctype_name}`
		WHERE company=%s AND branch=%s AND {link_field}=%s
		AND service_datetime=%s AND status!='Cancelled'
		""",
		(company, branch, resource_name, service_datetime),
	)[0][0] or 0
	return {"capacity": int(capacity), "used": int(used), "available": int(capacity) - int(used)}


def _ensure_customer_for_request(req_doc: TourismOnlineBookingRequest) -> str:
	"""
	Keep conversion deterministic: map email -> Customer if exists, else create one.
	"""
	email = (req_doc.email or "").strip().lower()
	if not email:
		frappe.throw(_("Email is required to create a customer."))

	existing = frappe.db.get_value("Customer", {"email_id": email}, "name")
	if existing:
		return existing

	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": req_doc.customer_name,
			"customer_type": "Individual",
			"customer_group": _get_default_customer_group(),
			"territory": _get_default_territory(),
			"email_id": email,
			"mobile_no": req_doc.phone,
		}
	)
	customer.insert(ignore_permissions=True)
	return customer.name


def _get_default_customer_group():
	val = None
	if frappe.db.exists("DocType", "Selling Settings"):
		val = frappe.db.get_single_value("Selling Settings", "customer_group")
	if val and frappe.db.exists("Customer Group", val):
		return val
	# fallback to first non-group root
	return (
		frappe.db.get_value("Customer Group", {"is_group": 0}, "name", order_by="lft asc")
		or frappe.db.get_value("Customer Group", {}, "name", order_by="lft asc")
		or "All Customer Groups"
	)


def _get_default_territory():
	val = None
	if frappe.db.exists("DocType", "Selling Settings"):
		val = frappe.db.get_single_value("Selling Settings", "territory")
	if val and frappe.db.exists("Territory", val):
		return val
	return (
		frappe.db.get_value("Territory", {"is_group": 0}, "name", order_by="lft asc")
		or frappe.db.get_value("Territory", {}, "name", order_by="lft asc")
		or "All Territories"
	)


def _optional_filters(d):
	return {k: v for k, v in (d or {}).items() if v not in (None, "", [])}


def _is_room_available(unit, check_in_date, check_out_date, exclude_booking=None):
	if not unit or not check_in_date or not check_out_date:
		return True
	rows = frappe.get_all(
		"Tourism Booking",
		filters=[
			["unit", "=", unit],
			["status", "!=", "Cancelled"],
			["check_in_date", "<", check_out_date],
			["check_out_date", ">", check_in_date],
		],
		fields=["name"],
		limit_page_length=2,
	)
	for row in rows:
		if not exclude_booking or row.name != exclude_booking:
			return False
	return True

