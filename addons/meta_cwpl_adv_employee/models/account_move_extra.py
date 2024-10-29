# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime


class ExtraAccountMove(models.Model):
    _inherit="account.move"
    
    employee_advance_source = fields.Many2one(comodel_name="employee.advance",string="Employee Advance Source",readonly=True)


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    is_advance_account = fields.Boolean('Is Advance Account', default=False)