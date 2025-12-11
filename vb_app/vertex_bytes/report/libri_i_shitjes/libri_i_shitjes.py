import frappe
from frappe import _

def execute(filters=None):
    if not filters: filters = {}

    columns = [
        {"label": _("Data"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Nr. Fatures"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
        {"label": _("Klienti"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Nr. Fiskal"), "fieldname": "company_tax_id", "fieldtype": "Data", "width": 120},
        {"label": _("Qarkullimi i Tatueshem (Baza)"), "fieldname": "taxable_turnover", "fieldtype": "Currency", "width": 140},
        {"label": _("TVSH 18%"), "fieldname": "vat_18", "fieldtype": "Currency", "width": 120},
        {"label": _("TVSH 8%"), "fieldname": "vat_8", "fieldtype": "Currency", "width": 120},
        {"label": _("Eksport / 0%"), "fieldname": "export_zero", "fieldtype": "Currency", "width": 120},
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
            si.posting_date,
            si.name,
            si.customer_name,
            si.company_tax_id,
            
            (si.base_net_total * IF(si.is_return, -1, 1)) as taxable_turnover,

            (SELECT IFNULL(SUM(tax_amount), 0)
             FROM `tabSales Taxes and Charges` st 
             WHERE st.parent = si.name AND st.rate = 18) * IF(si.is_return, -1, 1) as vat_18,

            (SELECT IFNULL(SUM(tax_amount), 0)
             FROM `tabSales Taxes and Charges` st 
             WHERE st.parent = si.name AND st.rate = 8) * IF(si.is_return, -1, 1) as vat_8,

            (
              (si.base_net_total * IF(si.is_return, -1, 1)) - 
              ((SELECT IFNULL(SUM(tax_amount), 0) FROM `tabSales Taxes and Charges` WHERE parent = si.name AND rate = 18) / 0.18 * IF(si.is_return, -1, 1)) -
              ((SELECT IFNULL(SUM(tax_amount), 0) FROM `tabSales Taxes and Charges` WHERE parent = si.name AND rate = 8) / 0.08 * IF(si.is_return, -1, 1))
            ) as export_zero,

            (si.base_grand_total * IF(si.is_return, -1, 1)) as total

        FROM
            `tabSales Invoice` si
        WHERE
            si.docstatus = 1
            AND si.company = %(company)s
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY
            si.posting_date ASC
    """

    data = frappe.db.sql(sql, filters, as_dict=True)
    return columns, data