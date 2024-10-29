from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class AccountMoveInheritCustomView(models.Model):
    _inherit = 'account.move'

    proceed_for_payment = fields.Boolean(string="Proceed for Payment", default=False)

    def action_register_payment(self):
        for rec in self:
            if rec.move_type == 'in_invoice' and not rec.proceed_for_payment:
                raise UserError(_('Please Select Proceed Payment! Then Click Register Payment, Bill NO: %s') % (rec.name))
            else:
                return super().action_register_payment()

    def action_proceed_payment(self):
        for rec in self:
            rec.proceed_for_payment = True
