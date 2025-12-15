/* apps/vb_app/vb_app/public/js/company_override.js */

frappe.ui.form.on("Company", {
    setup: function(frm) {
        override_chart_logic();
    },
    refresh: function(frm) {
        override_chart_logic();
        
        // CRITICAL FIX: Use setTimeout to run this AFTER standard ERPNext scripts
        // ERPNext often hides this section based on 'is_group' or save status.
        // We wait 100ms to override it back to visible.
        setTimeout(() => {
            force_expand_address_section(frm);
        }, 100);
    }
});

function force_expand_address_section(frm) {
    // CORRECTED FIELD NAME based on your screenshot
    const section_fieldname = 'company_info'; 
    
    if (frm.fields_dict[section_fieldname]) {
        const section = frm.fields_dict[section_fieldname];
        
        // 1. Force Display Programmatically
        // We clear 'depends_on' so Frappe doesn't auto-hide it again
        frm.set_df_property(section_fieldname, 'depends_on', '');
        frm.set_df_property(section_fieldname, 'hidden', 0);
        
        // We strictly tell the form to show it
        frm.toggle_display(section_fieldname, true);
        
        // 2. Force Expand & Lock
        if (section.collapse_link) {
            // If currently collapsed, trigger click to open
            if (section.wrapper.find('.section-body').is(':hidden')) {
                section.collapse_link.trigger('click');
            }
            
            // Hide the collapse arrow so it cannot be closed
            section.collapse_link.hide();
        }
        
        // CSS fallback to ensure visibility
        section.wrapper.find('.section-body').show();
    }
}

function override_chart_logic() {
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
                            
                            // 1. FILTER: Remove empty lines
                            var clean_options = r.message.filter(function(opt) {
                                return opt != null && opt.trim() !== "";
                            });

                            if (cur_frm) {
                                // 2. Update Options
                                cur_frm.set_df_property("chart_of_accounts", "options", clean_options.join("\n"));
                                
                                // 3. Make Mandatory to remove empty first option (Standard Frappe behavior)
                                cur_frm.set_df_property("chart_of_accounts", "reqd", 1);

                                // 4. Auto-select Logic
                                // If user hasn't picked one, pick "Kosova" or the first available
                                if (!selected_value || !clean_options.includes(selected_value)) {
                                    let target = clean_options.find(opt => opt.includes("Kosova")) || clean_options[0];
                                    cur_frm.set_value("chart_of_accounts", target);
                                }
                            }
                        }
                    },
                });
            }
        };
    }
}