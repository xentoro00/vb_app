// apps/vb_app/vb_app/public/js/company_override.js

frappe.ui.form.on("Company", {
    refresh: function(frm) {
        // We override the core ERPNext function here.
        // Because this file loads AFTER the core company.js, this override wins.
        
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
                                set_field_options("chart_of_accounts", r.message.join("\n"));
                                
                                 if (selected_value && in_list(r.message, selected_value)) {
                                    cur_frm.set_value("chart_of_accounts", selected_value);
                                } 
                                
                                else {
                                    cur_frm.set_value("chart_of_accounts", r.message[0]);
                                }
                            }
                        },
                    });
                }
            };
        }
    }
});