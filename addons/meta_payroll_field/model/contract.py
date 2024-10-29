from odoo import fields, models, api


class PayRollCustomizations(models.Model):
    _inherit = 'hr.contract'

    mobile_allowance = fields.Float(string="Mobile Allowance")
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user",
                          copy=False, compute="get_barcode")

    def get_barcode(self):
        self.barcode = self.employee_id.barcode
