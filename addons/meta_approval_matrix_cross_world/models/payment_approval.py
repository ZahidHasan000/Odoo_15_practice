
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PaymentApproval(models.Model):
    _inherit = 'account.payment'

    def send_to_checker(self):
        for rec in self:
            rec.write({'state': 'check'})

    def check_user_send_to_approve(self):
        for rec in self:
            rec.write({'state': 'to approve'})

    def check_user_cancel(self):
        for rec in self:
            rec.action_cancel()

    def approve_user_send_to_signed(self):
        for rec in self:
            rec.write({'state': 'signed'})

    def approve_user_cancel(self):
        for rec in self:
            rec.action_cancel()

    # def cross_function_user_cancel(self):
    #     for rec in self:
    #         rec.button_cancel()