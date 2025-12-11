__version__ = "0.0.1"


from frappe.core.doctype.data_import.exporter import Exporter
from vb_app.overrides.export_logic import (
    custom_build_response,
    generate_libri_i_shitjes_kuartale_excel,
    generate_libri_i_shitjes_tvsh_excel,
    generate_libri_blerjes_kuartale_excel,
    generate_libri_i_blerjes_tvsh_excel
)

Exporter.build_response = custom_build_response

Exporter.generate_libri_i_shitjes_kuartale_excel = generate_libri_i_shitjes_kuartale_excel
Exporter.generate_libri_i_shitjes_tvsh_excel = generate_libri_i_shitjes_tvsh_excel
Exporter.generate_libri_blerjes_kuartale_excel = generate_libri_blerjes_kuartale_excel
Exporter.generate_libri_i_blerjes_tvsh_excel = generate_libri_i_blerjes_tvsh_excel


from frappe.printing.doctype.letter_head.letter_head import LetterHead
from vb_app.overrides.custom_letter_head import (
    custom_validate,
    custom_set_image,
    custom_set_image_as_html
)
LetterHead.validate = custom_validate
LetterHead.set_image = custom_set_image
LetterHead.set_image_as_html = custom_set_image_as_html



# import frappe.telemetry
# from vb_app.overrides.telemetry import custom_init_telemetry, custom_capture_doc

# # Override the functions in memory
# frappe.telemetry.init_telemetry = custom_init_telemetry
# frappe.telemetry.capture_doc = custom_capture_doc