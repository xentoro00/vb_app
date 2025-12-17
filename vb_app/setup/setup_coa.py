import frappe
import os
import shutil

def run():
    
    # 1. Define Paths
    # Source is inside this app (vb_app)
    source_path = frappe.get_app_path("vb_app", "data", "xk_chart_of_accounts.json")
    
    # Destination is inside ERPNext (Standard 'verified' charts folder)
    # We construct this path carefully using frappe.get_app_path
    dest_folder = frappe.get_app_path("erpnext", "accounts", "doctype", "account", "chart_of_accounts", "verified")
    dest_path = os.path.join(dest_folder, "xk_chart_of_accounts.json")
    
    # 2. Safety Checks
    if not os.path.exists(source_path):
        print(f"❌ Source file not found at: {source_path}")
        return

    if not os.path.exists(dest_folder):
        print(f"❌ ERPNext chart folder not found at: {dest_folder}")
        return

    # 3. Copy if missing or modified
    try:
        # We copy it every time to ensure updates apply
        shutil.copy(source_path, dest_path)
        print(f"✅ Copied Chart of Accounts to ERPNext verified folder.")
    except Exception as e:
        print(f"❌ Failed to copy chart: {e}")