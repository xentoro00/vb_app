import frappe
import sys

def run():
    """
    Reverts the Company Injection:
    1. Removes custom 'company' fields.
    2. Removes custom 'company_split_section' breaks.
    3. Removes 'default_company' from User.
    """
    print("\n🧹 Running Cleanup Script...")

    # The specific fieldnames we want to destroy
    TARGET_FIELDS = ["company", "company_split_section", "default_company"]

    # Find all Custom Field records that match these names
    # We fetch the 'name' (ID of the Custom Field record) and 'dt' (Parent DocType)
    custom_fields = frappe.get_all(
        "Custom Field", 
        filters={"fieldname": ["in", TARGET_FIELDS]}, 
        fields=["name", "dt", "fieldname"]
    )

    total = len(custom_fields)
    print(f"Found {total} custom fields to remove.")

    if total == 0:
        print("✅ Nothing to clean up.")
        return

    count = 0
    bar_width = 40

    for i, field in enumerate(custom_fields):
        # Progress Bar Logic
        progress = (i + 1) / total
        filled = int(bar_width * progress)
        bar = "=" * filled + " " * (bar_width - filled)
        percent = int(progress * 100)
        sys.stdout.write(f"\r[{bar}] {percent}%")
        sys.stdout.flush()

        try:
            # We use delete_doc because it handles metadata clearing better than db.delete
            # "Custom Field" is the DocType we are deleting rows from
            frappe.delete_doc("Custom Field", field.name, force=1, ignore_permissions=True)
            count += 1
        except Exception as e:
            # If it fails, print a small error but keep going
            sys.stdout.write("\033[K") # Clear line
            print(f"\n❌ Error removing {field.fieldname} from {field.dt}: {e}")

    print(f"\n\n✅ Successfully removed {count} custom fields.")
    
    print("🔄 Clearing cache to apply changes...")
    frappe.clear_cache()
    frappe.db.commit()
    print("✨ Done.")