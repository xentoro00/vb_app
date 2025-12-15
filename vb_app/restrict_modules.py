import frappe

def run():
    """
    Removes DocPerm, Page Role, and Workspace permissions for roles 
    that are not explicitly allowed in HR and Payroll modules.
    """
    print("🚀 Running Module Role Restriction (Docs, Pages, Workspaces)...")

    # 1. Define Allowed Roles per Module Category
    ALWAYS_ALLOWED = ["Administrator", "System Manager", "VB Admin"]

    # Roles for "HR" Profile
    ALLOWED_HR = ALWAYS_ALLOWED + [
        "HR User", "HR Manager", "Leave Approver", "Expense Approver", 
        "Fleet Manager", "Employee" 
    ]

    # Roles for "HR", "Finance", "Accounting" Profiles
    ALLOWED_PAYROLL = ALWAYS_ALLOWED + [
        "HR User", "HR Manager", "Payroll Manager", 
        "Accounts User", "Accounts Manager", "Auditor"
    ]

    # 2. Define Module Mapping
    MODULE_CONFIG = {
        "HR": ["HR", "Human Resources"],
        "Payroll": ["Payroll"]
    }

    # 3. Process
    for config_name, module_names in MODULE_CONFIG.items():
        allowed_roles = ALLOWED_HR if config_name == "HR" else ALLOWED_PAYROLL
        
        # --- A. DOCTYPES ---
        doctypes = frappe.get_all("DocType", filters={"module": ["in", module_names]}, pluck="name")
        doc_perm_count = 0
        for dt in doctypes:
            perms_to_delete = frappe.get_all("DocPerm", {
                "parent": dt,
                "role": ["not in", allowed_roles]
            }, pluck="name")

            if perms_to_delete:
                frappe.db.delete("DocPerm", {"name": ["in", perms_to_delete]})
                doc_perm_count += len(perms_to_delete)
        print(f"✅ Cleaned {config_name} DocTypes: Removed {doc_perm_count} rules.")

        # --- B. PAGES (Dashboards/Reports Views) ---
        # Fixed: Page roles use 'Has Role' table, not 'Page Role'
        pages = frappe.get_all("Page", filters={"module": ["in", module_names]}, pluck="name")
        page_role_count = 0
        for pg in pages:
            page_perms_to_delete = frappe.get_all("Has Role", {
                "parent": pg,
                "parenttype": "Page", 
                "role": ["not in", allowed_roles]
            }, pluck="name")

            if page_perms_to_delete:
                frappe.db.delete("Has Role", {"name": ["in", page_perms_to_delete]})
                page_role_count += len(page_perms_to_delete)
        print(f"✅ Cleaned {config_name} Pages: Removed {page_role_count} rules.")

        # --- C. WORKSPACES (Sidebar Items) ---
        # We fetch by module, but also explicitly force the Workspace named "Payroll" or "HR" 
        # to be processed, even if its module is set oddly in the DB.
        workspaces = frappe.get_all("Workspace", filters={"module": ["in", module_names]}, pluck="name")
        
        # Force include the workspace if it matches the config name (e.g. "Payroll")
        if config_name not in workspaces and frappe.db.exists("Workspace", config_name):
            workspaces.append(config_name)

        ws_role_count = 0
        for ws in workspaces:
            # 1. WIPE: Delete ALL roles for this workspace
            frappe.db.delete("Has Role", {
                "parent": ws,
                "parenttype": "Workspace"
            })

            # 2. RESET: Add back only the allowed roles
            # This ensures the workspace is strictly locked and never public.
            for role in allowed_roles:
                if not frappe.db.exists("Role", role): 
                    continue
                
                try:
                    frappe.get_doc({
                        "doctype": "Has Role",
                        "parent": ws,
                        "parenttype": "Workspace",
                        "role": role
                    }).insert(ignore_permissions=True)
                    ws_role_count += 1
                except Exception:
                    pass

        print(f"✅ Cleaned {config_name} Workspaces: Reset with {ws_role_count} allowed roles.")

    frappe.db.commit()
    frappe.clear_cache()