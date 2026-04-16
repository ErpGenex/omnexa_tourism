frappe.query_reports["Tourism Service Profitability"] = {
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

