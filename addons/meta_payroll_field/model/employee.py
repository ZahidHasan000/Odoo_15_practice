from odoo import fields, models, api


class EmployeeCustomizations(models.Model):
    _inherit = 'hr.employee'

    name_for_pay_slip = fields.Char(string="Name for Pay Slip")
    bank_name = fields.Char(string="Bank Name", compute="get_bank_name")
    bank_advice_type = fields.Selection([('beftn', 'BEFTN'), ('fund', 'Fund Transfer')], string="Bank Advice Type")

    def get_bank_name(self):
        if self.bank_account_id:
            self.bank_name = self.bank_account_id.bank_id.name
        else:
            self.bank_name = ""


class PayslipCustomizations(models.Model):
    _inherit = 'hr.payslip'

    name_for_pay_slip = fields.Char(string="Name for Pay Slip", compute="get_name")


    def get_name(self):
        for i in self:
            i.name_for_pay_slip = i.employee_id.name_for_pay_slip
