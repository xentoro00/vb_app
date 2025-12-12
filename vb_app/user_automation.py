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