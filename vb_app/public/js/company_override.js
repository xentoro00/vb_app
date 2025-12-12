/* apps/vb_app/vb_app/public/js/company_override.js */

frappe.ui.form.on("Company", {
	setup: function (frm) {
		// Override logic immediately when form initializes
		override_chart_logic();
	},
	refresh: function (frm) {
		// Ensure override persists on refresh
		override_chart_logic();

		// Force Address & Contact section to be open and uncollapsable
		force_expand_address_section(frm);
	},
});

function force_expand_address_section(frm) {
	// 1. Locate the section by fieldname "address_and_contact"
	// Note: Sections are often wrapper divs around the fields.
	// Frappe stores section breaks in fields_dict.

	if (frm.fields_dict["address_and_contact"]) {
		const section = frm.fields_dict["address_and_contact"];

		// Force Expand
		if (section.collapse_link) {
			// If it's currently collapsed, expand it
			if (section.wrapper.find(".section-body").is(":hidden")) {
				section.collapse_link.trigger("click");
			}

			// Hide the collapse arrow/link so user cannot close it
			section.collapse_link.hide();
		}

		// Ensure the section body is visible directly via CSS just in case
		section.wrapper.find(".section-body").show();
	}
}

function override_chart_logic() {
	// Safety check to ensure we are in the ERPNext environment
	if (erpnext && erpnext.company) {
		erpnext.company.set_chart_of_accounts_options = function (doc) {
			var selected_value = doc.chart_of_accounts;

			if (doc.country) {
				return frappe.call({
					method: "erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country",
					args: {
						country: doc.country,
						with_standard: true,
					},
					callback: function (r) {
						if (!r.exc && r.message && r.message.length > 0) {
							// 1. FILTER: Remove empty/null strings to prevent the blank first option
							var clean_options = r.message.filter(function (opt) {
								return opt != null && opt.trim() !== "";
							});

							// 2. Set the options using standard Frappe method
							// Passing options as a newline-separated string
							if (window.set_field_options) {
								set_field_options("chart_of_accounts", clean_options.join("\n"));
							} else if (cur_frm) {
								cur_frm.set_df_property(
									"chart_of_accounts",
									"options",
									clean_options.join("\n")
								);
							}

							// 3. LOGIC: Auto-select
							if (selected_value && clean_options.includes(selected_value)) {
								// If the user already selected something valid, keep it
								cur_frm.set_value("chart_of_accounts", selected_value);
							} else if (clean_options.length > 0) {
								// ELSE: Auto-select the FIRST option (e.g., Kosova)
								cur_frm.set_value("chart_of_accounts", clean_options[0]);
							}
						}
					},
				});
			}
		};
	}
}
