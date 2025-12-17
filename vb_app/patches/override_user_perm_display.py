import frappe
from frappe.permissions import add_permission, update_permission_property

def execute():
    # RELOAD: Ensure the core User doctype is up to date before modifying it
    frappe.reload_doc("core", "doctype", "user")
    
    # ==================================================================
    # PART 1: CREATE ROLE (If Missing)
    # ==================================================================
    role_name = "User Admin"
    
    if not frappe.db.exists("Role", role_name):
        new_role = frappe.new_doc("Role")
        new_role.role_name = role_name
        new_role.desk_access = 1  # Give Desk Access
        new_role.save(ignore_permissions=True)
        print(f"   + Created new Role: {role_name}")
    else:
        print(f"   ✓ Role '{role_name}' already exists.")

    # ==================================================================
    # PART 2: PROPERTY SETTERS (Field Visibility & Levels)
    # ==================================================================
    
    # 1. Override 'depends_on' for Roles Section (sb1) to stop auto-hiding
    frappe.make_property_setter({
        "doctype": "User",
        "doctype_or_field": "DocField",
        "fieldname": "sb1",
        "property": "depends_on",
        "value": "eval:doc.enabled == 1",
        "is_system_generated": 0
    })

    # 2. Override 'depends_on' for Modules Section (sb_allow_modules)
    frappe.make_property_setter({
        "doctype": "User",
        "doctype_or_field": "DocField",
        "fieldname": "sb_allow_modules",
        "property": "depends_on",
        "value": "eval:1",
        "is_system_generated": 0
    })

    # 3. Set 'Role Profile' Permission Level to 2
    frappe.make_property_setter({
        "doctype": "User",
        "doctype_or_field": "DocField",
        "fieldname": "role_profile_name",
        "property": "permlevel",
        "value": 2,             # <--- CHANGED: Passed as Integer
        "property_type": "Int", # <--- CHANGED: Capital 'I' is safer
        "is_system_generated": 0
    })
    # ==================================================================
    # PART 3: ROLE PERMISSIONS (User Admin Rules)
    # ==================================================================
    
    doctype = "User"

    # -- Rule A: Level 0 (View Only) --
    if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role_name, "permlevel": 0}):
        add_permission(doctype, role_name, 0)
        # Reset to Read-Only
        update_permission_property(doctype, role_name, 0, "write", 0)
        update_permission_property(doctype, role_name, 0, "create", 0)
        update_permission_property(doctype, role_name, 0, "delete", 0)
        update_permission_property(doctype, role_name, 0, "read", 1)
        print(f"   + Added Level 0 (Read Only) permission for {role_name}")
    else:
        # Enforce Read Only if it exists
        update_permission_property(doctype, role_name, 0, "write", 0)
        update_permission_property(doctype, role_name, 0, "read", 1)

    # -- Rule B: Level 2 (Edit Role Profile) --
    if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role_name, "permlevel": 2}):
        add_permission(doctype, role_name, 2)
        # Enable Write
        update_permission_property(doctype, role_name, 2, "write", 1)
        update_permission_property(doctype, role_name, 2, "read", 1)
        print(f"   + Added Level 2 (Read/Write) permission for {role_name}")
    else:
        # Enforce Write if it exists
        update_permission_property(doctype, role_name, 2, "write", 1)

    print("✅ User Form, Role, & Permissions updated successfully.")