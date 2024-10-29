from odoo import fields, models, api


class EmployeeCustomizations(models.Model):
    _inherit = 'hr.contract'

    car_allowance = fields.Float(string="Car Allowance")
    variable_pay = fields.Float(string="Variable Pay")
    recreation_allowance = fields.Float(string="Recreation Allowance")
    ex_gratia = fields.Float(string="Ex-Gratia")
    # joining_date = fields.Date(string="Joining Date")
