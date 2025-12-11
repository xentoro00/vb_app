frappe.query_reports["Libri i Shitjes"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1,
            "read_only": 0, // Changed to 0
        },
        {
            "fieldname": "period_filter",
            "label": __("Select Period"),
            "fieldtype": "Select",
            "options": ["This Month", "Last Month", "Last 3 Months", "Last 6 Months", "This Year", "Custom"],
            "default": "This Month",
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
            "on_change": function(query_report) {
                handle_custom_date_change(query_report);
            }
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1,
            "on_change": function(query_report) {
                handle_custom_date_change(query_report);
            }
        }
    ],

    "onload": function(report) {
        let period = report.get_filter_value("period_filter");
        report.is_programmatic_update = true;
        set_dates_by_period(report, period);
        setTimeout(() => { report.is_programmatic_update = false; }, 500);
    }
};

function handle_custom_date_change(report) {
    if (report.is_programmatic_update) {
        return;
    }
    if (report.get_filter_value("period_filter") !== "Custom") {
        report.set_filter_value("period_filter", "Custom");
    }
}

function set_dates_by_period(report, period) {
    let today = frappe.datetime.get_today();
    let current_month_start = frappe.datetime.month_start(); 
    let from_date, to_date;

    if (period === "This Month") {
        from_date = current_month_start;
        to_date = frappe.datetime.month_end();
    } else if (period === "Last Month") {
        from_date = frappe.datetime.add_months(current_month_start, -1);
        to_date = frappe.datetime.add_days(current_month_start, -1);
    } else if (period === "Last 3 Months") {
        from_date = frappe.datetime.add_months(current_month_start, -3);
        to_date = today;
    } else if (period === "Last 6 Months") {
        from_date = frappe.datetime.add_months(current_month_start, -6);
        to_date = today;
    } else if (period === "This Year") {
        from_date = frappe.datetime.year_start(today);
        to_date = frappe.datetime.year_end(today);
    } else {
        return;
    }

    report.set_filter_value("from_date", from_date);
    report.set_filter_value("to_date", to_date);
    report.refresh();
}