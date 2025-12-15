import frappe
import sys

def run():
    """
    1. Adds a 'Company' Custom Field to almost all standard DocTypes.
    2. Adds 'Default Company' Custom Field to User DocType.
    Runs automatically after the app is installed.
    """
    print("\n🚀 Running Company Field Injection Script...")

    # --- PART 1: GENERIC COMPANY FIELD ---
    FIELD_NAME = "company"
    
    # Modules to strict skip (System/Core internals)
    SKIP_MODULES = [
        "Core", "Custom", "Desk", "Email", "Integrations", 
        "Website", "Social", "Data Migration", "Geo", "Printing", "Scheduler"
    ]
    
    # DocTypes to specifically ignore for the generic 'company' field
    SKIP_DOCTYPES = [
        "User", "Role", "Has Role", "DocType", "Module Def", "Version", 
        "Error Log", "Scheduled Job Type", "Activity Log", "Patch Log"
    ]

    # Get all Standard (non-custom), Non-Single, Non-Table DocTypes
    doctypes = frappe.get_all("DocType", 
        filters={"custom": 0, "istable": 0, "issingle": 0}, 
        fields=["name", "module"]
    )

    total_docs = len(doctypes)
    print(f"Scanning {total_docs} DocTypes for injection...")

    count = 0
    skipped = 0
    
    # Simple progress bar logic
    for i, dt in enumerate(doctypes):
        try:
            # 1. Safety Checks
            if dt.module in SKIP_MODULES or dt.name in SKIP_DOCTYPES:
                skipped += 1
                continue

            # 2. Check if field exists (either as standard or custom)
            if frappe.db.exists("DocField", {"parent": dt.name, "fieldname": FIELD_NAME}) or \
               frappe.db.exists("Custom Field", {"dt": dt.name, "fieldname": FIELD_NAME}):
                skipped += 1
                continue

            # 3. Create the Custom Field
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": dt.name,
                "fieldname": FIELD_NAME,
                "label": "Company",
                "fieldtype": "Link",
                "options": "Company",
                "insert_after": "owner", # Places it near the top
                "hidden": 1,             # User cannot see it
                "read_only": 1,          # User cannot edit it
                "no_copy": 1,            # Don't copy this when duplicating docs
                "default": ""            # Relies on 'User Permissions' default
            })
            
            # Use module 'Vertex Bytes' so these export with your fixtures automatically
            custom_field.module = "Vertex Bytes" 
            custom_field.insert()
            
            count += 1
            
            # Print progress every 10 items or at the end
            if count % 10 == 0:
                sys.stdout.write(f"\r   -> Added to {count} DocTypes...")
                sys.stdout.flush()
                
        except Exception as e:
            print(f"\n❌ Error on {dt.name}: {e}")

    print(f"\r✅ Added 'company' field to {count} DocTypes. (Skipped/Existing: {skipped})")

    # --- PART 2: SPECIFIC USER FIELD (Default Company) ---
    print("\n👉 Checking User DocType for 'default_company'...")
    try:
        if not frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "default_company"}):
            user_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "User",
                "fieldname": "default_company",
                "label": "Default Company",
                "fieldtype": "Link",
                "options": "Company",
                "insert_after": "last_name", # Put it in the main section
                "reqd": 0,                   # Optional initially
                "allow_in_quick_entry": 1
            })
            user_field.module = "Vertex Bytes"
            user_field.insert()
            print("   -> Created 'default_company' field on User.")
        else:
            print("   -> Field 'default_company' already exists on User.")
            
    except Exception as e:
        print(f"❌ Error adding field to User: {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("✅ Setup Company Script Complete.\n")