from odoo import fields, models, api


class PayRollCustomizations(models.Model):
    _inherit = 'hr.payslip'

    job_id = fields.Many2one('hr.job', 'Job Position',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", compute="get_job_id")
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user",
                          copy=False, compute="get_barcode")
    new_title = fields.Char(compute="get_title")

    def get_title(self):
        for i in self:
            a = i.name.find("-")
            i.new_title = i.name[:a]

    def get_barcode(self):
        for i in self:
            print("barcode prodb", i.employee_id.barcode)
            i.barcode = i.employee_id.barcode

    def get_job_id(self):
        for i in self:
            i.job_id = i.employee_id.job_id
