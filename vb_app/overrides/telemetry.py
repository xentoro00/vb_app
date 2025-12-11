import frappe
from frappe.utils import getdate
from frappe.utils.caching import site_cache

# 1. Re-implement site_age (since we need it for your print logic)
@site_cache(ttl=60 * 60 * 12)
def site_age():
    try:
        est_creation = frappe.db.get_value("User", "Administrator", "creation")
        return (getdate() - getdate(est_creation)).days + 1
    except Exception:
        pass

# 2. Your Empty Init Function (Disables connection)
def custom_init_telemetry():
    """Init posthog for server side telemetry."""
    return

# 3. Your Custom Capture Logic
def custom_capture_doc(doc, action):
    # We use a try/except block to be safe
    try:
        age = site_age()
        # FIXED: Use f-string or str(age) to avoid TypeError
        print(f"age: {age}")

        if doc.get("__islocal") or not doc.get("name"):
            frappe.telemetry.capture("document_created", "frappe", properties={"doctype": doc.doctype, "action": "Insert"})
        else:
            frappe.telemetry.capture("document_modified", "frappe", properties={"doctype": doc.doctype, "action": action})
    except Exception:
        pass