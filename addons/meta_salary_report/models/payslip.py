from odoo import api, fields, models, _


class PayslipInherit(models.Model):
    _inherit = "hr.payslip"
    _order = "bank_order asc"

    bank_advice_type = fields.Text(string="Bank Advice Type", compute="get_bank_advice")
    bank_order = fields.Integer(compute="get_bank_advice", store=True)

    def get_bank_advice(self):
        for i in self:
            if i.employee_id.bank_advice_type:
                if i.employee_id.bank_advice_type == "fund":
                    i.bank_advice_type = "Fund Transfer"
                    if not i.bank_order:
                        i.bank_order = 2
                elif i.employee_id.bank_advice_type == "beftn":
                    i.bank_advice_type = "BEFTN"
                    if not i.bank_order:
                        i.bank_order = 1
            else:
                i.bank_advice_type = " "
                if not i.bank_order:
                    i.bank_order = 3