import frappe

def say_hello(doc, method):
    frappe.msgprint(f"Success! Your custom app intercepted the save for: {doc.title}")