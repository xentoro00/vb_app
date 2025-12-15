frappe.ui.form.on('Item', {
    company: function(frm) {
        // 1. Loop through the "Item Defaults" table rows
        $.each(frm.doc.item_defaults || [], function(i, row) {
            
            // Update the Company in the row to match the new selection
            frappe.model.set_value(row.doctype, row.name, 'company', frm.doc.company);
            
            // Clear the Warehouse in the row (since it might belong to the old company)
            frappe.model.set_value(row.doctype, row.name, 'default_warehouse', '');
        });
        
        // Refresh the table so the user sees the changes
        frm.refresh_field('item_defaults');
    },

    refresh: function(frm) {
        // 2. Filter the Warehouse dropdown in the Child Table
        // This ensures that when they click "Default Warehouse" inside the table,
        // they ONLY see warehouses for the selected company.
        
        frm.fields_dict['item_defaults'].grid.get_field('default_warehouse').get_query = function(doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
    }
});