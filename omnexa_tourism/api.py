from __future__ import annotations

import frappe


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("tourism", scenario=scenario, params=params)


@frappe.whitelist(allow_guest=True)
def get_site_config() -> dict:
	"""Public tourism website configuration."""
	return {
		"brand_name_ar": "Omnexa Tourism",
		"brand_name_en": "Omnexa Tourism",
		"tagline_ar": "اكتشف العالم معنا",
		"tagline_en": "Discover the world with us",
		"hero_text_ar": "من الفنادق الفاخرة إلى الرحلات الجوية — كل ما تحتاجه لرحلة لا تُنسى",
		"hero_text_en": "From luxury hotels to flights — everything you need for an unforgettable journey",
		"hero_image": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1920&q=85",
		"logo": "/assets/omnexa_tourism/logo.png",
		"primary_color": "#00bcd4",
		"secondary_color": "#0097a7",
		"accent_color": "#00bcd4",
		"gold_color": "#ffc107",
		"destinations": [
			{"key": "hotels", "name_ar": "فنادق", "name_en": "Hotels", "icon": "🏨", "desc": "Luxury stays"},
			{"key": "flights", "name_ar": "رحلات جوية", "name_en": "Flights", "icon": "✈️", "desc": "Global destinations"},
			{"key": "beaches", "name_ar": "شواطئ", "name_en": "Beaches", "icon": "🏖️", "desc": "Coastal paradise"},
			{"key": "activities", "name_ar": "أنشطة", "name_en": "Activities", "icon": "🎯", "desc": "Adventures"},
		],
		"services": [
			{"icon": "🏨", "ar": "حجز فنادق", "en": "Hotel Booking"},
			{"icon": "✈️", "ar": "تذاكر طيران", "en": "Flight Tickets"},
			{"icon": "🚗", "ar": "تأجير سيارات", "en": "Car Rental"},
			{"icon": "🎫", "ar": "أنشطة ترفيهية", "en": "Entertainment"},
			{"icon": "🍽️", "ar": "حجوزات مطاعم", "en": "Restaurant Reservations"},
			{"icon": "📱", "ar": "تطبيق المسافر", "en": "Traveler App"},
		],
		"stats": {"destinations": 100, "travelers": 50000, "partners": 200, "years": 12},
	}
