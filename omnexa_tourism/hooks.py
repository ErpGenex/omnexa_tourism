app_name = "omnexa_tourism"
app_title = "ErpGenEx — Tourism"
app_publisher = "ErpGenEx"
app_description = "Tourism vertical"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core", "omnexa_accounting"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "omnexa_tourism",
		"logo": "/assets/omnexa_tourism/tourism.svg",
		"title": "Tourism",
		"route": "/app/tourism",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_tourism/css/omnexa_tourism.css"
# app_include_js = "/assets/omnexa_tourism/js/omnexa_tourism.js"

# include js, css files in header of web template
# web_include_css = "/assets/omnexa_tourism/css/omnexa_tourism.css"
# web_include_js = "/assets/omnexa_tourism/js/omnexa_tourism.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_tourism/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_tourism/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_tourism.utils.jinja_methods",
# 	"filters": "omnexa_tourism.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "omnexa_tourism.install.enforce_supported_frappe_version"
before_migrate = "omnexa_tourism.install.enforce_supported_frappe_version"
after_install = "omnexa_tourism.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "omnexa_tourism.uninstall.before_uninstall"
# after_uninstall = "omnexa_tourism.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_tourism.utils.before_app_install"
# after_app_install = "omnexa_tourism.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_tourism.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_tourism.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "omnexa_tourism.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Tourism Booking": "omnexa_tourism.permissions.tourism_booking_query_conditions",
	"Tourism Room Unit": "omnexa_tourism.permissions.tourism_room_unit_query_conditions",
	"Tourism Room Type": "omnexa_tourism.permissions.tourism_room_type_query_conditions",
	"Tourism Operation Model": "omnexa_tourism.permissions.tourism_operation_model_query_conditions",
	"Tourism Hotel": "omnexa_tourism.permissions.tourism_hotel_query_conditions",
	"Tourism Hotel Floor": "omnexa_tourism.permissions.tourism_hotel_floor_query_conditions",
	"Tourism Guest Folio": "omnexa_tourism.permissions.tourism_guest_folio_query_conditions",
	"Tourism Charge Entry": "omnexa_tourism.permissions.tourism_charge_entry_query_conditions",
	"Tourism Service Order": "omnexa_tourism.permissions.tourism_service_order_query_conditions",
	"Tourism Travel Vendor": "omnexa_tourism.permissions.tourism_travel_vendor_query_conditions",
	"Tourism Travel Package": "omnexa_tourism.permissions.tourism_travel_package_query_conditions",
	"Tourism Package Booking": "omnexa_tourism.permissions.tourism_package_booking_query_conditions",
	"Tourism Transport Booking": "omnexa_tourism.permissions.tourism_transport_booking_query_conditions",
	"Tourism Flight Booking": "omnexa_tourism.permissions.tourism_flight_booking_query_conditions",
	"Tourism Activity Booking": "omnexa_tourism.permissions.tourism_activity_booking_query_conditions",
	"Tourism Housekeeping Task": "omnexa_tourism.permissions.tourism_housekeeping_task_query_conditions",
	"Tourism Vendor Contract": "omnexa_tourism.permissions.tourism_vendor_contract_query_conditions",
	"Tourism Pricing Rule": "omnexa_tourism.permissions.tourism_pricing_rule_query_conditions",
	"Tourism Online Booking Request": "omnexa_tourism.permissions.tourism_online_booking_request_query_conditions",
	"Tourism Beach Booking": "omnexa_tourism.permissions.tourism_beach_booking_query_conditions",
	"Tourism Restaurant Reservation": "omnexa_tourism.permissions.tourism_restaurant_reservation_query_conditions",
	"Tourism Restaurant Venue": "omnexa_tourism.permissions.tourism_restaurant_venue_query_conditions",
	"Tourism Beach Facility": "omnexa_tourism.permissions.tourism_beach_facility_query_conditions",
}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Tourism Booking": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Room Unit": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Room Type": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Operation Model": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Hotel": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Hotel Floor": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Guest Folio": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Charge Entry": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
		"on_update": "omnexa_tourism.accounting_integration.post_charge_entry_journal",
	},
	"Tourism Service Order": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Travel Vendor": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Travel Package": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Package Booking": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Transport Booking": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Flight Booking": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Vendor Contract": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Pricing Rule": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Online Booking Request": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Beach Booking": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Restaurant Reservation": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Restaurant Venue": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Beach Facility": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Activity Booking": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
	"Tourism Housekeeping Task": {
		"before_validate": "omnexa_tourism.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_tourism.permissions.enforce_branch_access_for_doc",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": ["omnexa_tourism.tasks.hourly"],
	"daily": ["omnexa_tourism.tasks.daily"],
}

# Testing
# -------

# before_tests = "omnexa_tourism.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_tourism.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_tourism.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
after_migrate = ["omnexa_tourism.install.after_migrate"]

before_request = ["omnexa_tourism.license_gate.before_request"]
# after_request = ["omnexa_tourism.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_tourism.utils.before_job"]
# after_job = ["omnexa_tourism.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_tourism.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

