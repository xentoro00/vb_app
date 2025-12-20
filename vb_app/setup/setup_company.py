import frappe
import sys

def run():
    """
    1. Forces 'company' to be the very first field (Mandatory, Editable).
    2. Forces 'company_split_section' to be immediately after 'company'.
    3. Pushes all original fields into the 'Details' section.
    """
    print("\n🚀 Running Strict Company Injection...")

    FIELD_NAME = "company"
    BREAK_NAME = "company_split_section"
    
    # Modules to skip
    SKIP_MODULES = [
        "Core", "Custom", "Desk", "Email", "Integrations", 
        "Website", "Social", "Data Migration", "Geo", "Printing", "Scheduler"
    ]
    
    # DocTypes to skip
    SKIP_DOCTYPES = [
        "User", "Role", "Has Role", "DocType", "Module Def", "Version", "Item",
        "Error Log", "Scheduled Job Type", "Activity Log", "Patch Log"
    ]

    doctypes = frappe.get_all("DocType", 
        filters={"custom": 0, "istable": 0, "issingle": 0}, 
        fields=["name", "module"]
    )

    total_docs = len(doctypes)
    count = 0
    bar_width = 40
    
    for i, dt in enumerate(doctypes):
        # Progress Bar
        progress = (i + 1) / total_docs
        filled = int(bar_width * progress)
        bar = "=" * filled + " " * (bar_width - filled)
        percent = int(progress * 100)
        sys.stdout.write(f"\r[{bar}] {percent}%")
        sys.stdout.flush()

        try:
            if dt.module in SKIP_MODULES or dt.name in SKIP_DOCTYPES:
                continue

            meta = frappe.get_meta(dt.name)
            has_company = meta.has_field(FIELD_NAME)

            # -------------------------------------------------------
            # STEP 1: POSITION THE COMPANY FIELD (Top of Page)
            # -------------------------------------------------------
            if has_company:
                # If field exists (Standard or Custom), Force properties
                # We update these even if they exist, to ensure order is correct.
                create_property_setter(dt.name, FIELD_NAME, "previous_field", "owner")
                create_property_setter(dt.name, FIELD_NAME, "reqd", 1)
                create_property_setter(dt.name, FIELD_NAME, "read_only", 0)
                create_property_setter(dt.name, FIELD_NAME, "hidden", 0)
            else:
                # If missing, Create Custom Field anchored to 'owner'
                if not frappe.db.exists("Custom Field", {"dt": dt.name, "fieldname": FIELD_NAME}):
                    frappe.get_doc({
                        "doctype": "Custom Field",
                        "dt": dt.name,
                        "fieldname": FIELD_NAME,
                        "label": "Company",
                        "fieldtype": "Link",
                        "options": "Company",
                        "insert_after": "owner", # Anchors to very top
                        "reqd": 1,
                        "read_only": 0,
                        "no_copy": 1,
                        "allow_on_submit": 1
                    }).insert()

            # -------------------------------------------------------
            # STEP 2: POSITION THE SECTION BREAK (Immediately After)
            # -------------------------------------------------------
            # Check if our specific section break exists
            break_exists = frappe.db.exists("Custom Field", {"dt": dt.name, "fieldname": BREAK_NAME})

            if not break_exists:
                # Create it
                frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": dt.name,
                    "fieldname": BREAK_NAME,
                    "label": "",
                    "fieldtype": "Section Break",
                    "insert_after": FIELD_NAME, # Anchor to company
                    "collapsible": 0
                }).insert()
            else:
                # If it exists, FORCE it to snap back to 'company'
                # (This fixes cases where other fields might have moved in between)
                frappe.db.set_value("Custom Field", {"dt": dt.name, "fieldname": BREAK_NAME}, "insert_after", FIELD_NAME)

            count += 1
                
        except Exception as e:
            sys.stdout.write("\033[K") 
            if "Duplicate entry" not in str(e):
                print(f"\n❌ Error on {dt.name}: {e}")

    # -------------------------------------------------------
    # STEP 3: USER DEFAULT COMPANY
    # -------------------------------------------------------
    setup_user_field()
    
    frappe.db.commit()
    frappe.clear_cache()
    print(f"\n✅ Processed {count} DocTypes. Layout enforced.")


def create_property_setter(doctype, fieldname, property, value):
    """Creates or Updates a Property Setter"""
    if not frappe.db.exists("Property Setter", {
        "doc_type": doctype, "field_name": fieldname, "property": property
    }):
        frappe.make_property_setter({
            "doctype": doctype,
            "doctype_or_field": "DocField",
            "fieldname": fieldname,
            "property": property,
            "value": value,
            "property_type": "Check" if isinstance(value, int) else "Data"
        })
    else:
        # If the setter exists but has the wrong value/position, update it!
        frappe.db.set_value("Property Setter", 
            {"doc_type": doctype, "field_name": fieldname, "property": property},
            "value", value
        )

def setup_user_field():
    # Helper to ensure User field exists
    try:
        if not frappe.db.exists("Custom Field", {"dt": "User", "fieldname": "default_company"}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "User",
                "fieldname": "default_company",
                "label": "Default Company",
                "fieldtype": "Link",
                "options": "Company",
                "insert_after": "email",
                "reqd": 1, 
                "allow_in_quick_entry": 1
            }).insert()
    except Exception:
        pass