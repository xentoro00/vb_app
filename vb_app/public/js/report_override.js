/* my_custom_app/public/js/override_export.js */

console.log("🔥🔥 EXPORT OVERRIDE: Script Loaded");

frappe.provide('frappe.views');

// --- 1. Custom Dialog Definition ---
const custom_get_export_dialog = function(report_name, extra_fields, callback) {
    const fields = [
        {
            label: __("File Format"),
            fieldname: "file_format",
            fieldtype: "Select",
            options: ["Excel"], // CSV REMOVED
            default: "Excel",
            reqd: 1,
        },
        {
            label: __("Export in Background"),
            fieldname: "export_in_background",
            fieldtype: "Check",
        }
    ];

    if (extra_fields) {
        fields.push({
            fieldtype: "Section Break",
            fieldname: "extra_fields",
            collapsible: 0,
        }, ...extra_fields);
    }

    const dialog = new frappe.ui.Dialog({
        title: __("Export Report: {0}", [report_name]),
        fields: fields,
        primary_action_label: __("Download"),
        primary_action: (data) => {
            const report_name_clean = report_name.trim();
            const custom_reports = [
                "Libri i Shitjes", 
                "Libri i Blerjes", 
                "Libri i Shitjes - 3 mujor", 
                "Libri i Blerjes - 3 mujor"
            ];

            if (custom_reports.includes(report_name_clean)) {
                 // Your Custom Python Call
                 // Ensure we get filters from the current report instance
                 let filters = {};
                 if (frappe.query_report) {
                     filters = frappe.query_report.get_filter_values();
                 }

                 let args = {
                        cmd: "vb_app.report_handlers.export_custom_excel", 
                        report_name: report_name_clean,
                        filters: JSON.stringify(filters)
                    };

                 open_url_post(frappe.request.url, args);
            } else {
                 callback(data);
            }
            dialog.hide();
        },
    });

    dialog.show();
};

// --- 2. The Button Hunter ---
const hijack_ui_button = function() {
    if (!frappe.query_report || !frappe.query_report.page) return false;

    // Look for the button in the standard menu dropdown
    // Note: We search for the text "Export" (translated)
    let $export_btn = frappe.query_report.page.wrapper
        .find('.menu-btn-group .dropdown-menu li a')
        .filter(function() { 
            // Check current text against "Export"
            return $(this).text().trim() === __("Export"); 
        });

    if ($export_btn.length > 0) {
        // Check if we already hijacked it to avoid double-binding
        if ($export_btn.attr('data-custom-hijacked') === 'true') {
            return true; // Already done
        }

        console.log("🔥🔥 EXPORT OVERRIDE: FOUND IT! Hijacking click handler now.");
        
        $export_btn.off('click'); // Remove old Frappe handler
        $export_btn.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("🔥🔥 EXPORT OVERRIDE: Button Clicked -> Opening Custom Dialog");
            
            let extra_fields = [];
            if (frappe.query_report.get_export_fields) {
                extra_fields = frappe.query_report.get_export_fields();
            }
            custom_get_export_dialog(frappe.query_report.report_name, extra_fields, (data) => {
                frappe.query_report.print_report(data.file_format, data);
            });
        });

        // Mark as done
        $export_btn.attr('data-custom-hijacked', 'true');
        return true; // Success!
    }
    
    return false; // Not found yet
};

// --- 3. The Supervisor (Runs repeatedly) ---
const start_watching = function() {
    // 1. Patch the internal method (Quick Fix)
    if (frappe.query_report && !frappe.query_report.is_custom_patched) {
        frappe.query_report.make_export = function() {
            let extra_fields = [];
            if (this.get_export_fields) {
                extra_fields = this.get_export_fields();
            }
            custom_get_export_dialog(this.report_name, extra_fields, (data) => {
                this.print_report(data.file_format, data);
            });
        };
        frappe.query_report.is_custom_patched = true;
        console.log("🔥🔥 EXPORT OVERRIDE: Internal Method Patched.");
    }

    // 2. Hunt for the UI Button (The Hard Fix)
    // We set up a poller that runs every 500ms for 10 seconds (20 attempts)
    let attempts = 0;
    const max_attempts = 20; 

    const interval = setInterval(() => {
        attempts++;
        const found = hijack_ui_button();
        
        if (found) {
            console.log(`🔥🔥 EXPORT OVERRIDE: UI Patch Complete on attempt ${attempts}. Stopping search.`);
            clearInterval(interval);
        } else {
            console.log(`🔥🔥 EXPORT OVERRIDE: Button search attempt ${attempts}/${max_attempts}... (Not found yet)`);
        }

        if (attempts >= max_attempts) {
            console.log("🔥🔥 EXPORT OVERRIDE: Gave up searching for button (Timeout).");
            clearInterval(interval);
        }
    }, 500);
};

$(document).ready(function() {
    // Run on initial load
    setTimeout(start_watching, 1000);

    // Run again whenever the user navigates
    frappe.router.on('change', () => {
        // Reset internal flag to allow re-patching on new reports
        if(frappe.query_report) frappe.query_report.is_custom_patched = false;
        setTimeout(start_watching, 1000);
    });
});