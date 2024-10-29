from odoo import fields, models, api


class PayRollSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    rule_name = fields.Char('Rule Name')
    pdf_rule_seq=fields.Integer(string="Report SL.")