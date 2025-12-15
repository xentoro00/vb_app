import frappe

def run():
    print("🚀 Running manual Property Setter application for Company...")

    properties = [
        # Standard Fields
        ("Company", "default_currency", "default", "Data", "EUR"),
        ("Company", "country", "default", "Data", "Kosovo"),
        
        # Chart of Accounts
        ("Company", "create_chart_of_accounts_based_on", "options", "Small Text", "Standard Template\nExisting Company"),
        ("Company", "create_chart_of_accounts_based_on", "reqd", "Check", "1"),
        ("Company", "create_chart_of_accounts_based_on", "default", "Data", "Standard Template"),

        # --- CORRECTED SECTION TARGET: company_info ---
        # Address & Contact Collapsible: false (0)
        ("Company", "company_info", "collapsible", "Check", "0"),
        
        # Address & Contact Display Depends On: empty (None)
        ("Company", "company_info", "depends_on", "Data", None),

        # Company Logo Hidden: false (0)
        ("Company", "company_logo", "hidden", "Check", "0"),
        
        # Company Logo Required: true (1)
        ("Company", "company_logo", "reqd", "Check", "1"),
    ]

    for dt, field_name, prop, prop_type, value in properties:
        try:
            # Clean up old/wrong entries first
            frappe.db.delete("Property Setter", {
                "doc_type": dt,
                "field_name": field_name,
                "property": prop
            })
            
            doc = frappe.get_doc({
                "doctype": "Property Setter",
                "doc_type": dt,
                "doctype_or_field": "DocField",
                "field_name": field_name,
                "property": prop,
                "property_type": prop_type,
                "value": value
            })
            doc.insert(ignore_permissions=True)
            print(f"   -> Applied: {dt}.{field_name}.{prop} = {value}")

        except Exception as e:
            print(f"❌ Failed to apply Property Setter for {dt}.{field_name}.{prop}: {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("✅ Property Setter application complete.")