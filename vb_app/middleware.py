import frappe
import json

def force_company_restriction():
    """
    Middleware to restrict data access based on ALL allowed companies.
    Only applies to DocTypes that actually have a 'company' field.
    """
    user = frappe.session.user
    print("----------------------")
    print(user)
    print("System Manager" in frappe.get_roles(user))
    print(frappe.get_roles(user))
    # 1. Bypass logic
    if user == "Guest":
        return
    if "System Manager" in frappe.get_roles(user):
        return

    # 2. IDENTIFY THE DOCTYPE
    # Most Desk API calls (get_list, reportview, search_link) pass 'doctype'
    doctype = frappe.form_dict.get("doctype")
    
    # If we don't know the DocType, or if the DocType doesn't have a 'company' field,
    # we MUST stop. Otherwise, we break system pages (like User, Role, etc).
    if not doctype:
        return

    try:
        # Check metadata (cached and fast)
        meta = frappe.get_meta(doctype)
        if not meta.has_field("company"):
            return
    except Exception:
        # If doctype is invalid, just return
        return

    # 3. FETCH ALL ALLOWED COMPANIES
    allowed_companies = frappe.get_all(
        "User Permission", 
        filters={"user": user, "allow": "Company"}, 
        pluck="for_value"
    )

    if not allowed_companies:
        default_co = frappe.db.get_value("User", user, "default_company")
        if default_co:
            allowed_companies = [default_co]

    if not allowed_companies:
        return

    # 4. PREPARE VALUE (Single string or List)
    if len(allowed_companies) == 1:
        restriction_value = allowed_companies[0]
    else:
        restriction_value = ["in", allowed_companies]

    # 5. INJECT FILTER
    if "filters" in frappe.form_dict:
        filters = frappe.form_dict["filters"]
        
        is_json = False
        if isinstance(filters, str):
            try:
                filters = json.loads(filters)
                is_json = True
            except (ValueError, TypeError):
                return

        if isinstance(filters, dict):
            # Check if user requested a specific valid company
            requested_company = filters.get("company")
            
            # If they asked for a specific company, and they are allowed to see it, let it pass.
            # Otherwise, force the full list of allowed companies.
            
            # Note: We need to handle if requested_company is a simple string or a list/operator
            is_valid_request = False
            if requested_company and isinstance(requested_company, str) and requested_company in allowed_companies:
                is_valid_request = True
            
            if not is_valid_request:
                filters["company"] = restriction_value
            
            if is_json:
                frappe.form_dict["filters"] = json.dumps(filters)
            else:
                frappe.form_dict["filters"] = filters

    # Special handling for direct 'company' param (rare in standard desk, common in RPC)
    # Only apply if we are sure the target doctype has the field (checked above)
    if "company" in frappe.form_dict:
        requested_co = frappe.form_dict["company"]
        if requested_co not in allowed_companies:
             # Default to the first allowed company for simple string fields
            frappe.form_dict["company"] = allowed_companies[0]