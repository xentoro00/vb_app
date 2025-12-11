import frappe
from frappe.utils.nestedset import get_descendants_of

# 1. ROLES THAT BYPASS ALL CHECKS (Can see/edit Gjirafa, Elkos, ETC, everything)
GLOBAL_ROLES = ["System Manager", "Administrator", "VB Admin"]

# 2. ROLES THAT CAN ACCESS CHILD COMPANIES (ETC Admin -> Elkos)
TREE_ACCESS_ROLES = ["User Admin"]

def check_company_permission(doc, method):
    # Bypass for Administrator account
    if frappe.session.user == "Administrator": 
        return
    
    # Skip non-relevant doctypes
    if doc.doctype in [
        "User Permission", "Error Log", "Activity Log", 
        "Access Log", "Comment", "Version", "View Log",
        "Notification", "Communication", "ToDo", "Note"
    ]: 
        return

    user_roles = frappe.get_roles(frappe.session.user)

    # CHECK 1: IS USER GLOBAL?
    # If they have at least one Global role, let them pass.
    if any(role in GLOBAL_ROLES for role in user_roles):
        return 

    # ----------------------------------------------------------------
    # IF WE REACH HERE, THE USER IS RESTRICTED (STRICT ISOLATION)
    # ----------------------------------------------------------------

    request_type = "delete" if method == "on_trash" else "write"
    target_company = doc.get("company")
    
    if not target_company:
        frappe.throw(f"⛔ <b>Access Denied</b><br>You are restricted to Company-Only data.<br>You cannot {request_type} this Global record.")

    allowed_companies = frappe.get_all(
        "User Permission", 
        filters={"user": frappe.session.user, "allow": "Company"}, 
        pluck="for_value"
    )

    if not allowed_companies:
         frappe.throw(f"⛔ <b>Access Denied</b><br>No Company Permission found for your user.")

    # CHECK 2: DOES USER HAVE TREE ACCESS? (Parent -> Child)
    has_tree_access = any(role in TREE_ACCESS_ROLES for role in user_roles)

    if has_tree_access:
        # ALLOW: Exact Match OR Child Company
        if target_company in allowed_companies:
            return 

        is_child = False
        for parent in allowed_companies:
            descendants = get_descendants_of("Company", parent, ignore_permissions=True)
            if target_company in descendants:
                is_child = True
                break
        
        if not is_child:
             frappe.throw(f"⛔ <b>Access Denied (Tree Admin)</b><br>You cannot {request_type} records for <b>{target_company}</b>.")

    else:
        # ALLOW: Exact Match ONLY (Strict Isolation)
        if target_company not in allowed_companies:
            frappe.throw(f"⛔ <b>Access Denied</b><br>You can only {request_type} records for: <b>{', '.join(allowed_companies)}</b>.")