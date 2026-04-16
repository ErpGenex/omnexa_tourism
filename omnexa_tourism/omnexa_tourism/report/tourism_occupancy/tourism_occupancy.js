frappe.query_reports["Tourism Occupancy"] = {
	filters: [
		{
			fieldname: "date",
			label: __("Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Branch",
		},
	],
};

