import frappe

def auto_create_tax_templates(doc, method):
    """
    Runs on Account > After Insert.
    Creates Tax Templates when specific VAT accounts (220000, 130000) are created
    during Company setup or manual account creation.
    """
    # Only run for the specific VAT accounts defined in Kosova Chart of Accounts
    if doc.account_number == "220000":
        # Sales Tax Account Created -> Make Sales & Item Templates
        create_sales_tax_templates(doc.company, doc.name)
        create_item_tax_templates(doc.company, doc.name, "220000")

    elif doc.account_number == "130000":
        # Purchase Tax Account Created -> Make Purchase & Item Templates
        create_purchase_tax_templates(doc.company, doc.name)
        create_item_tax_templates(doc.company, doc.name, "130000")

def create_item_tax_templates(company, account_name, account_number):
    # Format: (Title, Rate, Account Number Link)
    ITEM_TAXES_DATA = [
        ("TVSH 18% Shitje", 18, "220000"),
        ("TVSH 8% Shitje", 8, "220000"),
        ("TVSH 0% Shitje", 0, "220000"),
        ("TVSH 18% Blerje", 18, "130000"),
        ("TVSH 8% Blerje", 8, "130000"),
        ("TVSH 0% Blerje", 0, "130000"),
    ]

    # Filter for taxes related to THIS specific account number
    relevant_taxes = [x for x in ITEM_TAXES_DATA if x[2] == account_number]
    
    for title, rate, _ in relevant_taxes:
        template_name = f"{title} - {company}"
        if not frappe.db.exists("Item Tax Template", template_name):
            try:
                new_doc = frappe.get_doc({
                    "doctype": "Item Tax Template",
                    "title": template_name,
                    "company": company,
                    "taxes": [{"tax_type": account_name, "tax_rate": rate}]
                })
                new_doc.insert(ignore_permissions=True)
                # frappe.msgprint(f"✅ Auto-created Item Tax: {template_name}")
            except Exception as e:
                frappe.log_error(f"Error creating Item Tax {template_name}: {str(e)}", "Tax Automation Error")

def create_sales_tax_templates(company, account_name):
    SALES_TAXES_DATA = [
        ("TVSH 18% Shitje", 18),
        ("TVSH 8% Shitje", 8),
        ("TVSH 0% Shitje", 0),
    ]

    for title, rate in SALES_TAXES_DATA:
        template_name = f"{title} - {company}"
        if not frappe.db.exists("Sales Taxes and Charges Template", template_name):
            try:
                new_doc = frappe.get_doc({
                    "doctype": "Sales Taxes and Charges Template",
                    "title": template_name,
                    "company": company,
                    "taxes": [{
                        "charge_type": "On Net Total", 
                        "account_head": account_name, 
                        "rate": rate, 
                        "description": title
                    }]
                })
                new_doc.insert(ignore_permissions=True)
                # frappe.msgprint(f"✅ Auto-created Sales Tax: {template_name}")
            except Exception as e:
                frappe.log_error(f"Error creating Sales Tax {template_name}: {str(e)}", "Tax Automation Error")

def create_purchase_tax_templates(company, account_name):
    PURCHASE_TAXES_DATA = [
        ("TVSH 18% Blerje", 18),
        ("TVSH 8% Blerje", 8),
        ("TVSH 0% Blerje", 0),
    ]

    for title, rate in PURCHASE_TAXES_DATA:
        template_name = f"{title} - {company}"
        if not frappe.db.exists("Purchase Taxes and Charges Template", template_name):
            try:
                new_doc = frappe.get_doc({
                    "doctype": "Purchase Taxes and Charges Template",
                    "title": template_name,
                    "company": company,
                    "taxes": [{
                        "charge_type": "On Net Total", 
                        "account_head": account_name, 
                        "rate": rate, 
                        "description": title
                    }]
                })
                new_doc.insert(ignore_permissions=True)
                # frappe.msgprint(f"✅ Auto-created Purchase Tax: {template_name}")
            except Exception as e:
                frappe.log_error(f"Error creating Purchase Tax {template_name}: {str(e)}", "Tax Automation Error")