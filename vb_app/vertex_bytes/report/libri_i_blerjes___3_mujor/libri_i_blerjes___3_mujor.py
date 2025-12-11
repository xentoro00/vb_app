import frappe
from frappe import _

def execute(filters=None):
    if not filters: filters = {}

    columns = [
        {"label": _("Data"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Nr. Brendshem"), "fieldname": "name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},
        {"label": _("Nr. Fatures Furnitorit"), "fieldname": "bill_no", "fieldtype": "Data", "width": 140},
        {"label": _("Furnitori"), "fieldname": "supplier_name", "fieldtype": "Data", "width": 150},
        {"label": _("Nr. Fiskal"), "fieldname": "tax_id", "fieldtype": "Data", "width": 120},
        {"label": _("Baza e Blerjeve"), "fieldname": "base_net_total", "fieldtype": "Currency", "width": 120},
        {"label": _("TVSH e Zbritshme 18%"), "fieldname": "vat_18", "fieldtype": "Currency", "width": 120},
        {"label": _("TVSH e Zbritshme 8%"), "fieldname": "vat_8", "fieldtype": "Currency", "width": 120},
        {"label": _("Import / Pa TVSH%"), "fieldname": "import_novat", "fieldtype": "Currency", "width": 120},
        {"label": _("Totale"), "fieldname": "total", "fieldtype": "Currency", "width": 120},
    ]

    # 1. Smart Default
    if not filters.get("company"):
        filters["company"] = frappe.defaults.get_user_default("Company")
    
    if not filters.get("company"):
        allowed = frappe.get_list("Company", pluck="name", limit=1)
        if allowed:
             filters["company"] = allowed[0]

    # 2. Security Check
    if filters.get("company") and not frappe.has_permission("Company", doc=filters.get("company")):
        frappe.throw(_("You do not have permission to view reports for Company: {0}").format(filters.get("company")))

    if not filters.get("company"):
        frappe.msgprint("Please select a Company.")
        return columns, []
        
    if not filters.get("from_date") or not filters.get("to_date"):
        return columns, []

    sql = """
        SELECT
            pi.posting_date,
            pi.name,
            pi.bill_no,
            pi.supplier_name,
            pi.tax_id,
            (pi.base_net_total * IF(pi.is_return, -1, 1)) as base_net_total,
            
            (SELECT IFNULL(SUM(tax_amount), 0)
             FROM `tabPurchase Taxes and Charges` pt 
             WHERE pt.parent = pi.name AND pt.rate = 18) * IF(pi.is_return, -1, 1) as vat_18,

            (SELECT IFNULL(SUM(tax_amount), 0)
             FROM `tabPurchase Taxes and Charges` pt 
             WHERE pt.parent = pi.name AND pt.rate = 8) * IF(pi.is_return, -1, 1) as vat_8,

            (
              (pi.base_net_total * IF(pi.is_return, -1, 1)) - 
              ((SELECT IFNULL(SUM(tax_amount), 0) FROM `tabPurchase Taxes and Charges` WHERE parent = pi.name AND rate = 18) / 0.18 * IF(pi.is_return, -1, 1)) -
              ((SELECT IFNULL(SUM(tax_amount), 0) FROM `tabPurchase Taxes and Charges` WHERE parent = pi.name AND rate = 8) / 0.08 * IF(pi.is_return, -1, 1))
            ) as import_novat,

            (pi.base_grand_total * IF(pi.is_return, -1, 1)) as total

        FROM
            `tabPurchase Invoice` pi
        WHERE
            pi.docstatus = 1
            AND pi.company = %(company)s
            AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY
            pi.posting_date ASC
    """

    data = frappe.db.sql(sql, filters, as_dict=True)
    return columns, data