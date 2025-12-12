import frappe

def auto_create_letterhead(doc, method):
    """
    Runs on Company > After Insert.
    Creates a Letter Head if the company has a logo.
    """
    # Check if the company has a logo uploaded
    if doc.company_logo:
        # 1. Define a unique name for the Letter Head
        lh_name = f"{doc.company_name} Official"
        
        # 2. Create the Letter Head Document
        try:
            new_lh = frappe.get_doc({
                "doctype": "Letter Head",
                "letter_head_name": lh_name,
                "source": "Image",  # Uses the standard image upload field
                "image": doc.company_logo,
                # "company" field logic:
                # If you have a custom field 'custom_company' on Letter Head, use that.
                # Standard Letter Head doesn't strictly belong to a company, but user permissions handle it.
                "is_default": 0 
            })
            
            # If you added a custom company field to Letter Head (from your previous work), set it here:
            if hasattr(new_lh, 'custom_company'):
                new_lh.custom_company = doc.name
            
            new_lh.insert(ignore_permissions=True)
            
            # 3. Link this new Letter Head back to the Company
            frappe.db.set_value("Company", doc.name, "default_letter_head", lh_name)
            
            frappe.msgprint(f"✅ Auto-created Letter Head: {lh_name}")

        except Exception as e:
            frappe.log_error(f"Failed to create letterhead for {doc.company_name}: {str(e)}", "Company Automation Error")

    else:
        # Optional: Notify that no logo was found
        pass