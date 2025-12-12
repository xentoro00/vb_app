import frappe

def run():
    """
    1. Creates 'VB Admin' Role if missing.
    2. Grants 'VB Admin' full access to almost all DocTypes.
    3. Preserves 'System Manager' access by copying standard perms to Custom DocPerms.
    """
    print("🚀 Running VB Admin Permission Setup...")

    # --- CONFIGURATION ---
    new_role = 'VB Admin'
    source_role = 'System Manager'
    doctypes_to_exclude = ['DocType', 'DocType Layout']
    # ---------------------

    # 0. CREATE ROLE IF MISSING
    if not frappe.db.exists("Role", new_role):
        print(f"Creating Role: {new_role}...")
        role_doc = frappe.new_doc("Role")
        role_doc.role_name = new_role
        role_doc.desk_access = 1
        role_doc.insert(ignore_permissions=True)
    else:
        print(f"Role '{new_role}' already exists.")

    print(f"--- Starting permission build for: {new_role} ---")
    print(f"--- Preserving permissions for: {source_role} ---")

    # 1. GET ALL DEFAULT PERMISSIONS FOR 'System Manager'
    # We use sql to be faster and get raw dicts
    default_perms = frappe.db.get_all('DocPerm', 
        filters={'role': source_role}, 
        fields=['*']
    )

    if not default_perms:
        print(f"[ERROR] No default permissions found for {source_role}. Cannot proceed.")
        return

    # 2. GET ALL UNIQUE DOCTYPES TO PROCESS
    print("Finding unique DocTypes...")
    doctypes_set = set()
    try:
        for d in default_perms:
            doctypes_set.add(d['parent'])
    except KeyError:
        print("[ERROR] A permission record is missing the 'parent' key. Aborting.")
        return

    doctypes_to_process = list(doctypes_set)
    print(f"Found {len(doctypes_to_process)} DocTypes to process...")

    perms_copied_vb = 0
    perms_copied_sm = 0

    # 3. LOOP THROUGH ALL DOCTYPES
    for doc_name in doctypes_to_process:
        
        # --- A: Handle VB Admin ---
        # Create its permissions (if not excluded)
        if doc_name not in doctypes_to_exclude:
            try:
                # Check if already exists to avoid unique constraint errors before insert
                if not frappe.db.exists("Custom DocPerm", {"role": new_role, "parent": doc_name}):
                    frappe.get_doc({
                        'doctype': 'Custom DocPerm',
                        'role': new_role,
                        'parent': doc_name,
                        'permlevel': 0,
                        'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1,
                        'cancel': 1, 'amend': 1, 'report': 1, 'export': 1, 'import': 1,
                        'share': 1, 'print': 1, 'email': 1, 'set_user_permissions': 1
                    }).insert(ignore_permissions=True)
                    perms_copied_vb += 1
            except Exception as e:
                print(f"[ERROR VB] Failed on {doc_name}: {e}")

        # --- B: Handle System Manager ---
        # We MUST create a Custom DocPerm for System Manager to preserve its access
        # because once a Custom DocPerm exists for a DocType, Standard perms might be ignored.
        
        # Find all its default perms for this DocType
        sm_perms_for_doctype = [d for d in default_perms if d['parent'] == doc_name]
        
        # Now, loop through just those perms and copy them
        for perm in sm_perms_for_doctype:
            # Check if this specific permission rule already exists in Custom DocPerm
            # We construct a filter based on critical fields to check duplication
            exists = frappe.db.exists("Custom DocPerm", {
                "role": source_role, 
                "parent": doc_name, 
                "permlevel": perm.get('permlevel', 0)
            })
            
            if exists:
                continue

            perm.pop('name', None)
            perm.pop('idx', None)
            perm.pop('owner', None)
            perm.pop('creation', None)
            perm.pop('modified', None)
            perm.pop('modified_by', None)
            
            new_sm_perm = perm.copy()
            new_sm_perm['doctype'] = 'Custom DocPerm'
            
            try:
                frappe.get_doc(new_sm_perm).insert(ignore_permissions=True)
                perms_copied_sm += 1
            except Exception as e:
                # Often fails if field names mismatch between DocPerm and Custom DocPerm
                # but usually they match.
                print(f'[ERROR SM] Failed to copy perm for {doc_name}: {e}')

    # 4. COMMIT ALL CHANGES
    frappe.db.commit()

    print('--- All operations complete. ---')
    print(f'Created {perms_copied_vb} permissions for {new_role}')
    print(f'Preserved {perms_copied_sm} permissions for {source_role}')