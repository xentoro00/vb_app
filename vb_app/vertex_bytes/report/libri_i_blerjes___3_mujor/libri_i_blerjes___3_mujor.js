frappe.query_reports["Libri i Blerjes - 3 mujor"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
			"read_only": 0 // Changed to 0
		},
		{
			"fieldname": "period_filter",
			"label": __("Select Period"),
			"fieldtype": "Select",
			"options": ["TM1", "TM2", "TM3", "TM4"],
			"default": "TM1",
			"reqd": 1,
			"on_change": function(query_report) {
				const period = query_report.get_filter_value("period_filter");
				query_report.is_programmatic_update = true;
				set_dates_by_period(query_report, period);
				setTimeout(() => { query_report.is_programmatic_update = false; }, 500);
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1,
			"read_only": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1,
			"read_only": 1
		}
	],

	"onload": function(report) {
		let period = report.get_filter_value("period_filter");
		if (period) {
			report.is_programmatic_update = true;
			set_dates_by_period(report, period);
			setTimeout(() => { report.is_programmatic_update = false; }, 500);
		}
	}
};

function set_dates_by_period(report, period) {
	let today = frappe.datetime.get_today();
	let year = today.split('-')[0]; 
	let from_date, to_date;

	if (period === "TM1") {
		from_date = year + "-01-01";
		to_date = year + "-03-31";
	} else if (period === "TM2") {
		from_date = year + "-04-01";
		to_date = year + "-06-30";
	} else if (period === "TM3") {
		from_date = year + "-07-01";
		to_date = year + "-09-30";
	} else if (period === "TM4") {
		from_date = year + "-10-01";
		to_date = year + "-12-31";
	} else {
		return; 
	}

	report.set_filter_value("from_date", from_date);
	report.set_filter_value("to_date", to_date);
	report.refresh();
}