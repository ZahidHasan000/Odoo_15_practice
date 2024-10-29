from odoo import api, fields, models, _


class ContractInherit(models.Model):
    _inherit = "hr.contract"

    grade_field = fields.Char(string="Grade field")

