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

def clear_company_data_on_trash(doc, method):
    lh_name = f"{doc.company_name} Official"

    if frappe.db.exists("Letter Head", lh_name):
        try:
            frappe.delete_doc("Letter Head", lh_name, force=1, ignore_permissions=True)
            # frappe.log_error(f"Deleted Letter Head: {lh_name}", "Cleanup Success")
        except Exception as e:
            frappe.log_error(f"Could not delete Letter Head {lh_name}: {str(e)}", "Cleanup Error")

    # --- PART 2: CLEANUP TAX TEMPLATES ---
    # The Tax creation script used "doc.name" (The Company ID)
    # We define the lists of titles to look for:
    ITEM_TAX_TITLES = [
        "TVSH 18% Shitje", "TVSH 8% Shitje", "TVSH 0% Shitje",
        "TVSH 18% Blerje", "TVSH 8% Blerje", "TVSH 0% Blerje"
    ]

    SALES_TAX_TITLES = [
        "TVSH 18% Shitje", "TVSH 8% Shitje", "TVSH 0% Shitje"
    ]

    PURCHASE_TAX_TITLES = [
        "TVSH 18% Blerje", "TVSH 8% Blerje", "TVSH 0% Blerje"
    ]

    # Helper function defined inside the script
    def delete_templates(doctype, titles, company_id):
        for title in titles:
            # Reconstruct the exact name: "Title - CompanyID"
            template_name = f"{title} - {company_id}"
            
            if frappe.db.exists(doctype, template_name):
                try:
                    frappe.delete_doc(doctype, template_name, force=1, ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Failed to delete {template_name}: {str(e)}", "Cleanup Error")

    # Run the cleanup function for all 3 types
    # Note: We pass 'doc.name' here because Tax Templates are usually linked by ID
    delete_templates("Item Tax Template", ITEM_TAX_TITLES, doc.name)
    delete_templates("Sales Taxes and Charges Template", SALES_TAX_TITLES, doc.name)
    delete_templates("Purchase Taxes and Charges Template", PURCHASE_TAX_TITLES, doc.name)