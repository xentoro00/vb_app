import frappe

def run():
    print("🚀 Running Item DocType Customization...")
    
    # 1. Disable Quick Entry (Property Setter on DocType)
    # allow_in_quick_entry = 0
    set_property("Item", None, "allow_in_quick_entry", "Check", "0")
    print("   -> Disabled Quick Entry for Item.")

    # 2. Add/Move Company Field to First Page
    # We place it after 'item_name' to ensure it's at the top of the main tab.
    field_name = "company"
    
    existing_field = frappe.db.get_value("Custom Field", {"dt": "Item", "fieldname": field_name}, "name")
    
    if existing_field:
        # If exists (e.g. created by old script), MOVE it and UNHIDE it
        doc = frappe.get_doc("Custom Field", existing_field)
        doc.insert_after = "item_name"
        doc.hidden = 0 
        doc.read_only = 1
        doc.save()
        print("   -> Moved 'company' field to first page (after item_name).")
    else:
        # Create new
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Item",
            "fieldname": field_name,
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "insert_after": "item_name", # First Page
            "hidden": 0,             # Visible
            "read_only": 1,          # Cannot be changed manually
            "no_copy": 1,
            "default": "",
            "module": "Vertex Bytes"
        }).insert()
        print("   -> Created 'company' field on Item.")

    frappe.db.commit()
    frappe.clear_cache()
    print("✅ Item Setup Complete.")

def set_property(dt, field, prop, prop_type, val):
    # Helper to set property setter safely
    if not frappe.db.exists("Property Setter", {"doc_type": dt, "property": prop}):
        frappe.get_doc({
            "doctype": "Property Setter",
            "doc_type": dt,
            "doctype_or_field": "DocType" if not field else "DocField",
            "field_name": field,
            "property": prop,
            "property_type": prop_type,
            "value": val,
            "module": "Vertex Bytes"
        }).insert(ignore_permissions=True)