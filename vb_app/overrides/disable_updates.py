import frappe

def disable_frappe_update_checks():
	"""
	Hard-disable Frappe / ERPNext update & changelog checks.
	Company-managed fork.
	"""

	import frappe.utils.change_log as cl

	def _no_update(*args, **kwargs):
		return frappe._dict(major=[], minor=[], patch=[])

	# Kill update check
	cl.check_for_update = _no_update

	# Kill popup
	cl.show_update_popup = lambda *a, **k: None

	# Kill redis flags
	cl.add_message_to_redis = lambda *a, **k: None

	# Kill notification flag check
	cl.has_app_update_notifications = lambda: False
