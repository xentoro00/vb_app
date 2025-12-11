import frappe
from frappe import _
from frappe.utils import flt, is_image

# 1. Custom Validate Method
def custom_validate(self):
    self.set_image()
    self.validate_disabled_and_default()

# 2. Custom Set Image Method
def custom_set_image(self):
    # Header Image Logic
    if self.source == "Image":
        self.set_image_as_html(
            field="image",
            width="image_width",
            height="image_height",
            align="align",
            html_field="content",
            dimension_prefix="image_",
            success_msg=_("Header HTML set from attachment {0}").format(self.image),
            failure_msg=_("Please attach an image file to set HTML for Letter Head."),
        )

    # Footer Image Logic (Your New Addition)
    if hasattr(self, "footer_source") and self.footer_source == "Image":
        self.set_image_as_html(
            field="footer_image",
            width="footer_image_width",
            height="footer_image_height",
            align="footer_align",
            html_field="footer",
            dimension_prefix="footer_image_",
            success_msg=_("Footer HTML set from attachment {0}").format(self.footer_image),
            failure_msg=_("Please attach an image file to set HTML for Footer."),
        )

# 3. Custom Set Image As HTML (Modified to accept arguments)
def custom_set_image_as_html(self, field, width, height, dimension_prefix, align, html_field, success_msg, failure_msg):
    if not self.get(field) or not is_image(self.get(field)):
        frappe.msgprint(failure_msg, alert=True, indicator="orange")
        return

    self.set(width, flt(self.get(width)))
    self.set(height, flt(self.get(height)))

    # Aspect ratio logic
    dimension = "width" if self.get(width) > self.get(height) else "height"
    dimension_value = self.get(f"{dimension_prefix}{dimension}")

    if not dimension_value:
        dimension_value = ""

    self.set(
        html_field,
        f"""<div style="text-align: {self.get(align, "").lower()};">
<img src="{self.get(field)}" alt="{self.get("name")}"
{dimension}="{dimension_value}" style="{dimension}: {dimension_value}px;">
</div>""",
    )
    frappe.msgprint(success_msg, alert=True)