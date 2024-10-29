from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class RegisterPayment(models.TransientModel):
    _inherit = 'account.payment.register'

    check_number = fields.Char(string="Check Number")

    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()
        # Make sure the account move linked to generated payment
        # belongs to the expected sales team
        # team_id field on account.payment comes from the `_inherits` on account.move model
        vals.update({'payment_check_number': self.check_number})
        return vals


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    payment_check_number = fields.Char(string="Check Number")
