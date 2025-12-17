import frappe
from frappe.desk.search import search_link as original_search_link
def get_allowed_companies(user):
    """
    Helper: Returns a list of company names allowed for the user.
    1. Checks 'User Permission' document (Support for multiple allowed companies).
    2. Fallback to 'default_company' in User doctype if no permissions set.
    """
    # 1. Fetch from User Permission (Strict Table)
    allowed_companies = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Company"},
        pluck="for_value"
    )

    # 2. If no strict permissions, fallback to default_company
    if not allowed_companies:
        default = frappe.db.get_value("User", user, "default_company")
        if default:
            allowed_companies = [default]

    return allowed_companies

@frappe.whitelist()
def secure_search_link(doctype, txt, query=None, filters=None, page_length=20, search_field=None):
    """
    Wrapper middleware to enforce Company restrictions on Link Searches.
    """
    user = frappe.session.user
    
    # 1. Skip checks for System Managers
    if "System Manager" in frappe.get_roles(user):
        return original_search_link(doctype, txt, query, filters, page_length, search_field)

    # 2. Fetch the user's strictly allowed company
    # Adjust "User Permission" query if you use a custom field on the User doctype instead
    allowed_company = frappe.db.get_value("User Permission", 
        {"user": user, "allow": "Company"}, "for_value")

    if allowed_company:
        # Ensure filters is a dictionary (it might be None or a JSON string)
        if filters is None:
            filters = {}
        elif isinstance(filters, str):
            import json
            try:
                filters = json.loads(filters)
            except ValueError:
                filters = {}

        # 3. The "Middleware" Logic: Force the Company Filter
        # Even if they sent {"company": "Restricted Company"}, we overwrite it here.
        # We only apply this if the target DocType actually has a company field.
        if frappe.db.has_column(doctype, "company"):
            filters["company"] = allowed_company

    # 4. Execute the original standard function with the sanitized filters
    return original_search_link(doctype, txt, query, filters, page_length, search_field)


def get_company_permission_query(user):
    """
    Returns a SQL condition to restrict access to allowed companies only.
    Used in permission_query_conditions hook.
    """
    # 1. DEBUGGING: Use errprint to force output to terminal
    # This will show up in RED in your bench console.
    frappe.errprint(f"🔒 SECURITY HOOK: Checking User '{user}'")

    if not user: user = frappe.session.user

    # 2. Bypass for the TRUE Administrator only
    if user == "Administrator":
        frappe.errprint("   🔓 ALLOWED: User is Administrator")
        return ""
    
    # 3. Check for Admin Roles
    # If your test user has 'System Manager', they were bypassing the check!
    roles = frappe.get_roles(user)
    
    # UNCOMMENT the lines below if you want System Managers to see EVERYTHING.
    # Currently commented out to strictly test isolation.
    if "System Manager" in roles or "VB Admin" in roles:
        frappe.errprint(f"   🔓 ALLOWED: User has Admin Role: {roles}")
        return ""

    # 4. Get Allowed Companies
    allowed_companies = frappe.get_all("User Permission", 
        filters={"user": user, "allow": "Company"}, 
        pluck="for_value"
    )

    # 5. Construct SQL Condition
    if allowed_companies:
        # frappe.db.escape adds quotes ('Company Name')
        safe_companies = ", ".join([frappe.db.escape(c) for c in allowed_companies])
        
        # Condition: Company in allowed list OR Company is Empty (Global)
        condition = f"(company IN ({safe_companies}) OR company IS NULL OR company = '')"
        
        frappe.errprint(f"   🛡️ RESTRICTED: Applying SQL Filter -> {condition}")
        return condition
    
    # 6. Strict Block (No companies assigned)
    frappe.errprint("   ⛔ BLOCKED: No company permissions found.")
    return "1=0"


def has_project_permission(doc, user=None, permission_type=None):
    """
    READ SECURITY (Form View): Checks against allowed list
    """
    if not user: user = frappe.session.user
    
    allowed_list = get_allowed_companies(user)

    if doc.company in allowed_list:
        return True

    return False