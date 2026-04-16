frappe.ui.form.on("Tourism Flight Booking", {
	refresh(frm) {
		frm.add_custom_button(__("Suggest Pricing"), async () => {
			if (!frm.doc.vendor || !frm.doc.from_airport || !frm.doc.to_airport) {
				frappe.msgprint(__("Please set Vendor, From (Airport) and To (Airport) first."));
				return;
			}
			if (!frm.doc.company || !frm.doc.branch || !frm.doc.customer) {
				frappe.msgprint(__("Please set Company, Branch and Customer first."));
				return;
			}

			const r = await frappe.call({
				method: "omnexa_tourism.omnexa_tourism.doctype.tourism_flight_booking.tourism_flight_booking.suggest_pricing",
				args: {
					company: frm.doc.company,
					branch: frm.doc.branch,
					customer: frm.doc.customer,
					vendor: frm.doc.vendor,
					from_airport: frm.doc.from_airport,
					to_airport: frm.doc.to_airport,
					trip_type: frm.doc.trip_type,
					cabin_class: frm.doc.cabin_class,
					posting_date: frappe.datetime.get_today(),
				},
			});

			const msg = r.message || {};
			const fare = msg.fare || {};
			const markup = msg.markup || {};

			if (!fare || Object.keys(fare).length === 0) {
				frappe.msgprint(__("No matching fare rule found in active vendor contracts."));
				return;
			}

			await frm.set_value("auto_price", 1);
			await frm.set_value("fare_basis", fare.fare_basis || frm.doc.fare_basis);
			await frm.set_value("base_fare", fare.base_fare || 0);
			await frm.set_value("taxes", fare.taxes || 0);
			await frm.set_value("fees", fare.fees || 0);
			if (fare.currency) {
				await frm.set_value("currency", fare.currency);
			}

			if (markup && markup.name) {
				await frm.set_value("markup_rule", markup.name);
				await frm.set_value("markup_type", markup.markup_type || "Percent");
				await frm.set_value("markup_value", markup.markup_value || 0);
			} else {
				await frm.set_value("markup_rule", null);
				await frm.set_value("markup_value", 0);
			}

			frm.refresh_fields([
				"auto_price",
				"markup_rule",
				"markup_type",
				"markup_value",
				"fare_basis",
				"base_fare",
				"taxes",
				"fees",
				"currency",
				"total_price",
				"markup_amount",
				"price",
			]);
		});
	},

	price(frm) {
		// if user manually adjusts billed price, stop auto pricing
		if (frm.doc.auto_price) {
			frm.set_value("auto_price", 0);
		}
	},
});

