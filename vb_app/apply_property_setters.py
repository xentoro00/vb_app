import frappe

def run():
    """
    Manually inserts Property Setter records to customize the Company DocType,
    bypassing the problematic fixture synchronization mechanism.
    """
    print("🚀 Running manual Property Setter application for Company...")

    properties = [
        # Default Currency: "EUR"
        ("Company", "default_currency", "default", "Data", "EUR"),
        
        # Country: "Kosovo"
        ("Company", "country", "default", "Data", "Kosovo"),
        
        # Create Chart Of Accounts Based On: Standard Template\nExisting Company
        ("Company", "create_chart_of_accounts_based_on", "options", "Small Text", "Standard Template\nExisting Company"),
        
        # FIX: Make "Create Based On" Mandatory to remove empty first option
        ("Company", "create_chart_of_accounts_based_on", "reqd", "Check", "1"),
        
        # FIX: Set Default to "Standard Template" explicitly
        ("Company", "create_chart_of_accounts_based_on", "default", "Data", "Standard Template"),

        # Address & Contact Collapsible: false (0)
        ("Company", "address_and_contact", "collapsible", "Check", "0"),
        
        # Address & Contact Display Depends On (JS): empty (null)
        ("Company", "address_and_contact", "depends_on", "Data", None),
    ]

    for dt, field_name, prop, prop_type, value in properties:
        try:
            # Delete existing property setter for a clean run
            frappe.db.delete("Property Setter", {
                "doc_type": dt,
                "field_name": field_name,
                "property": prop
            })
            
            # Insert the new property setter
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