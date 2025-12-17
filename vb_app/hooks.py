app_name = "vb_app"
app_title = "Vertex Bytes"
app_publisher = "Vertex Bytes Solution"
app_description = "Vertex Bytes Solution"
app_email = "erp@vertexbytes.net"
app_license = "mit"

# Apps
# ------------------
required_apps = ["frappe/hrms"]


# --- Asset Includes ---
# qetu i kallxon cilat mi shti qe jan ne folderin /public
# include js, css files in header of desk.html
# app_include_css = "/assets/vb_app/css/vb_app.css"
app_include_js = [
    "/assets/vb_app/js/data_exporter_override.js", 
    "/assets/vb_app/js/custom_request.js", 
    "/assets/vb_app/js/report_override.js",
]

# qeto jan client scripts
# include js in doctype views
doctype_js = {
    "Company": "public/js/company_override.js",
    "User": "public/js/user_override.js",
    "Item": "public/js/item_override.js"
}

# --- Document Events (Triggers) ---
# qeto evente ekzekutohen sa here te ndodh ndonje veprim (insert, update, delete)
# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "User": {
        "after_insert": "vb_app.automations.user_automation.auto_create_permission",
        "on_trash": "vb_app.automations.user_automation.cleanup_permission_on_delete"
    },
    "Company": {
        "after_insert": "vb_app.automations.company_automation.auto_create_letterhead",
        "on_trash": "vb_app.automations.company_automation.clear_company_data_on_trash",
        "on_update": "vb_app.automations.company_automation.update_letterhead_on_change",
    },
    "Account": {
        "after_insert": "vb_app.automations.tax_automation.auto_create_tax_templates"
    },
    "Project": {
        "validate": "my_security_app.my_security_app.security.validate_project_security"
    },
    "*": {
        # This adds your check to every document write
        "on_update": "vb_app.company_permission.check_company_permission",
        "on_submit": "vb_app.company_permission.check_company_permission",
        "on_cancel": "vb_app.company_permission.check_company_permission",
        "on_trash":  "vb_app.company_permission.check_company_permission",
    }
}

# --- API Overrides ---
override_whitelisted_methods = {
    "frappe.desk.query_report.run": "vb_app.report_handlers.secure_run_report",
    "frappe.desk.search.search_link": "vb_app.security.secure_search_link"
}

# Installation
# ------------
# --- Installation Hooks ---
# qeto bahen execute sit bahet install-app vb_app, dmth veq 1 her.
after_install = [
    "vb_app.setup.setup_company.run",
    "vb_app.setup.setup_permissions.run",
    "vb_app.setup.setup_item.run",
    "vb_app.apply_property_setters.run",
    "vb_app.setup.setup_coa.run"
]

# Includes in <head>
# ------------------
# --- Fixtures (Database Exports) ---
# fixtures jan ndryshimet ne doctype prsh nese eban mandatory ni field tani veq ja ban bench export-fixtures 
# edhe ti qet qeto ndryshime, qekjo ish e pshtjellt pak.
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Vertex Bytes"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Vertex Bytes"]]}
]
permission_query_conditions = {
    # Accounting
    "Sales Invoice": "vb_app.security.get_company_permission_query",
    "Purchase Invoice": "vb_app.security.get_company_permission_query",
    "Journal Entry": "vb_app.security.get_company_permission_query",
    "Payment Entry": "vb_app.security.get_company_permission_query",
    "Account": "vb_app.security.get_company_permission_query",
    "Cost Center": "vb_app.security.get_company_permission_query",
    "Budget": "vb_app.security.get_company_permission_query",
    "Asset": "vb_app.security.get_company_permission_query",
    
    # Selling
    "Quotation": "vb_app.security.get_company_permission_query",
    "Sales Order": "vb_app.security.get_company_permission_query",
    "Delivery Note": "vb_app.security.get_company_permission_query",
    "Customer": "vb_app.security.get_company_permission_query",
    
    # Buying
    "Supplier": "vb_app.security.get_company_permission_query",
    "Purchase Order": "vb_app.security.get_company_permission_query",
    "Purchase Receipt": "vb_app.security.get_company_permission_query",
    "Material Request": "vb_app.security.get_company_permission_query",
    "Request for Quotation": "vb_app.security.get_company_permission_query",
    "Supplier Quotation": "vb_app.security.get_company_permission_query",

    # Stock
    "Item": "vb_app.security.get_company_permission_query",
    "Stock Entry": "vb_app.security.get_company_permission_query",
    "Delivery Trip": "vb_app.security.get_company_permission_query",
    "Batch": "vb_app.security.get_company_permission_query",
    "Serial No": "vb_app.security.get_company_permission_query",
    "Warehouse": "vb_app.security.get_company_permission_query",
    "Stock Ledger Entry": "vb_app.security.get_company_permission_query",

    # HR & Payroll
    "Employee": "vb_app.security.get_company_permission_query",
    "Leave Application": "vb_app.security.get_company_permission_query",
    "Expense Claim": "vb_app.security.get_company_permission_query",
    "Salary Slip": "vb_app.security.get_company_permission_query",
    "Payroll Entry": "vb_app.security.get_company_permission_query",
    "Attendance": "vb_app.security.get_company_permission_query",
    "Shift Request": "vb_app.security.get_company_permission_query",
    "Job Offer": "vb_app.security.get_company_permission_query",

    # Projects
    "Project": "vb_app.security.get_company_permission_query",
    "Task": "vb_app.security.get_company_permission_query",
    "Timesheet": "vb_app.security.get_company_permission_query",
    "Activity Cost": "vb_app.security.get_company_permission_query",

    # Support
    "Issue": "vb_app.security.get_company_permission_query",
    "Warranty Claim": "vb_app.security.get_company_permission_query",
    
    # CRM
    "Lead": "vb_app.security.get_company_permission_query",
    "Opportunity": "vb_app.security.get_company_permission_query"
}



# # 2. For Form Views (Read Access)
has_permission = {
    "Project": "vb_app.security.has_project_permission"
}

# 3. For API Writes/Saves (Write Access) - ADD THIS

# include js, css files in header of web template
# web_include_css = "/assets/vb_app/css/vb_app.css"
# web_include_js = "/assets/vb_app/js/vb_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vb_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}


# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vb_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vb_app.utils.jinja_methods",
# 	"filters": "vb_app.utils.jinja_filters"
# }





# Uninstallation
# ------------

# before_uninstall = "vb_app.uninstall.before_uninstall"
# after_uninstall = "vb_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vb_app.utils.before_app_install"
# after_app_install = "vb_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vb_app.utils.before_app_uninstall"
# after_app_uninstall = "vb_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vb_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vb_app.tasks.all"
# 	],
# 	"daily": [
# 		"vb_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"vb_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vb_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vb_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vb_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vb_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vb_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vb_app.middleware.force_company_restriction"]
# after_request = ["vb_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["vb_app.utils.before_job"]
# after_job = ["vb_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vb_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

