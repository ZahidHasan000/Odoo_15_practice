# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime


class EmployeeAdvanceInherit(models.Model):
    _inherit = 'employee.advance'

    adjusted_amount = fields.Float('Adjusted Amount')

    @api.depends('ea_amount', 'adjusted_amount')
    def get_remaining_balance(self):
        for rec in self:
            rec['remaining_balance'] = rec.ea_amount - rec.adjusted_amount

    remaining_balance = fields.Float('Remaining Balance', compute="get_remaining_balance", default=0.00)

    def name_get(self):
        """ Display 'Advance amount in name' """
        res = []
        for adv in self:
            if adv.ea_amount > 0.0:
                amount = adv.ea_amount
                name = adv.name + ' (' + f'{amount:.2f}' + ')'
            else:
                name = adv.name
            res.append((adv.id, name))

        return res
