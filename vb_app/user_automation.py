import frappe

def auto_create_permission(doc, method):
    """
    Runs on User > After Insert.
    Creates a User Permission for the selected 'default_company'.
    """
    # Check if the administrator selected a company
    # Note: 'default_company' must be a custom field you added to User doctype
    if doc.get("default_company"):
        try:
            # Create the User Permission Document
            perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": doc.name,              # The new user's email
                "allow": "Company",            # The Document Type we are restricting
                "for_value": doc.default_company, # The specific company selected
                "is_default": 1,               # Set as default
                "apply_to_all_doctypes": 1,    # CRITICAL: Strict isolation
                "hide_descendants": 0
            })
            
            # Insert without checking permissions
            perm.insert(ignore_permissions=True)
            
            frappe.msgprint(
                f"🔒 Security: User strictly locked to <b>{doc.default_company}</b>"
            )

        except Exception as e:
            frappe.log_error(f"Failed to set permission for {doc.name}: {str(e)}", "User Automation Error")

def cleanup_permission_on_delete(doc, method):
    """
    Runs on User > On Trash (Before Delete).
    Deletes the User Permission associated with the default_company.
    """
    if doc.get("default_company"):
        # 1. Find the specific User Permission created for this company
        permission_name = frappe.db.get_value("User Permission", {
            "user": doc.name,
            "allow": "Company",
            "for_value": doc.default_company
        })

        # 2. If it exists, delete it
        if permission_name:
            try:
                frappe.delete_doc("User Permission", permission_name, ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Failed to delete permission for {doc.name}: {str(e)}", "Cleanup Error")