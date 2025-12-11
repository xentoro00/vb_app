frappe.provide("frappe.data_import");

// We define the patch logic in a separate function
function apply_data_exporter_patch() {
    if (frappe.data_import.DataExporter.prototype.is_patched_by_vb_app) {
        return; // Already patched, stop here
    }

    console.log("VB App: Applying DataExporter Patch...");

    // 1. OVERRIDE make_dialog
    frappe.data_import.DataExporter.prototype.make_dialog = function() {
        this.dialog = new frappe.ui.Dialog({
            title: __("Export Data"),
            fields: [
                {
                    fieldtype: "Select",
                    fieldname: "file_type",
                    label: __("File Type"),
                    options: ["Excel"], // CSV Removed
                    default: "Excel",
                },
                {
                    fieldtype: "Select",
                    fieldname: "export_records",
                    label: __("Export Type"),
                    options: [
                        { label: __("All Records"), value: "all" },
                        { label: __("Filtered Records"), value: "by_filter" },
                        { label: __("5 Records"), value: "5_records" },
                        { label: __("Blank Template"), value: "blank_template" },
                    ],
                    default: this.exporting_for === "Insert New Records" ? "blank_template" : "all",
                    change: () => {
                        this.update_record_count_message();
                    },
                },
                {
                    fieldtype: "HTML",
                    fieldname: "filter_area",
                    depends_on: (doc) => doc.export_records === "by_filter",
                },
                {
                    fieldtype: "Section Break",
                },
                {
                    fieldtype: "HTML",
                    fieldname: "select_all_buttons",
                },
                {
                    label: __(this.doctype),
                    fieldname: this.doctype,
                    fieldtype: "MultiCheck",
                    columns: 2,
                    on_change: () => this.update_primary_action(),
                    options: this.get_multicheck_options(this.doctype),
                    sort_options: false,
                },
                ...frappe.meta.get_table_fields(this.doctype).map((df) => {
                    let doctype = df.options;
                    let child_fieldname = df.fieldname;
                    let label = df.reqd
                        ? __('{0} ({1}) (1 row mandatory)', [__(df.label || df.fieldname, null, df.parent), __(doctype)])
                        : __("{0} ({1})", [__(df.label || df.fieldname, null, df.parent), __(doctype)]);
                    return {
                        label,
                        fieldname: child_fieldname,
                        fieldtype: "MultiCheck",
                        columns: 2,
                        on_change: () => this.update_primary_action(),
                        options: this.get_multicheck_options(doctype, child_fieldname),
                    };
                }),
            ],
            primary_action_label: __("Export"),
            primary_action: (values) => this.export_records(values),
            on_page_show: () => this.select_mandatory(),
        });

        this.make_filter_area();
        this.make_select_all_buttons();
        this.update_record_count_message();
        this.dialog.show();
    };

    // 2. OVERRIDE get_multicheck_options
    frappe.data_import.DataExporter.prototype.get_multicheck_options = function(doctype, child_fieldname = null) {
        if (!this.column_map) {
            this.column_map = get_columns_for_picker(this.doctype);
        }

        let autoname_field = null;
        let meta = frappe.get_meta(doctype);
        if (meta.autoname && meta.autoname.startsWith("field:")) {
            let fieldname = meta.autoname.slice("field:".length);
            autoname_field = frappe.meta.get_field(doctype, fieldname);
        }

        let fields = child_fieldname ? this.column_map[child_fieldname] : this.column_map[doctype];

        let is_field_mandatory = (df) => {
            if (this.doctype === "Sales Invoice" && !child_fieldname) {
                const required_invoice_fields = ["name", "posting_date", "customer", "company_tax_id", "total_qty", "grand_total"];
                if (required_invoice_fields.includes(df.fieldname)) return true;
            } 
            else if (this.doctype === "Purchase Invoice" && !child_fieldname) {
                const required_purchase_fields = ["name", "posting_date", "supplier", "company_tax_id", "tax_id", "grand_total"];
                if (required_purchase_fields.includes(df.fieldname)) return true;
            }
            else {
                if (df.reqd && this.exporting_for == "Insert New Records") return true;
                if (autoname_field && df.fieldname == autoname_field.fieldname) return true;
                if (df.fieldname === "name") return true;
                return false;
            }
        };

        return fields
            .filter((df) => {
                if ((this.doctype === "Sales Invoice" || this.doctype === "Purchase Invoice") && !is_field_mandatory(df)) return false;
                if (autoname_field && df.fieldname === "name") return false;
                return true;
            })
            .map((df) => {
                return {
                    label: __(df.label, null, df.parent),
                    value: df.fieldname,
                    danger: is_field_mandatory(df),
                    checked: false, 
                    description: `${df.fieldname} ${df.reqd ? __("(Mandatory)") : ""}`,
                };
            });
    };

    // Mark as patched so we don't run this twice
    frappe.data_import.DataExporter.prototype.is_patched_by_vb_app = true;
    console.log("VB App: DataExporter successfully patched.");
}

// 3. THE TRIGGER
// We listen for the export button click or page load, and force load the library
$(document).on('app_ready', function() {
    // We try to patch immediately if it's already there
    if (frappe.data_import && frappe.data_import.DataExporter) {
        apply_data_exporter_patch();
    }
});

// We also hook into the standard standard list view menu for 'Export'
// This ensures that when the user clicks 'Export', we load the file and THEN patch it
$(document).on('page-change', function() {
    // Whenever the user goes to a list view, we prepare the patch
    if (frappe.get_route()[0] === 'List') {
        frappe.require("data_import_tools.bundle.js", function() {
            if (frappe.data_import && frappe.data_import.DataExporter) {
                apply_data_exporter_patch();
            }
        });
    }
});

// Helper Function
function get_columns_for_picker(doctype) {
    let out = {};
    const meta = frappe.get_meta(doctype);
    
    // 1. Get standard fields (from meta.fields)
    let standard_fields = meta.fields.filter((df) => {
        return frappe.model.is_value_type(df.fieldtype) && !df.hidden;
    });

    // 2. MANUALLY ADD THE "ID" FIELD
    // This was missing! We force it to be the very first item.
    let system_fields = [
        {
            fieldname: "name",
            label: __("ID"),
            fieldtype: "Data",
            parent: doctype,
            reqd: 1 // Mark as mandatory so our other logic picks it up
        }
    ];

    // Combine them: ID first, then the rest
    out[doctype] = system_fields.concat(standard_fields);

    // 3. Handle Child Tables (Keep this the same)
    meta.fields
        .filter((df) => df.fieldtype === "Table")
        .forEach((df) => {
            const child_meta = frappe.get_meta(df.options);
            out[df.fieldname] = child_meta.fields.filter((df) => {
                return frappe.model.is_value_type(df.fieldtype) && !df.hidden;
            });
        });

    return out;
}