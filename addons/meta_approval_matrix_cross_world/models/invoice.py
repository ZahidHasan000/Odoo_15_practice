
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[
        ('draft', 'User'),
        ('check', 'Check'),
        ('to approve', 'Approved'),
        ('cross_function', 'Cross Function'),
        ('signed', 'Signed'),
        ('posted',),
        ('cancel',)
    ], ondelete={'draft': 'cascade', 'check': 'cascade', 'to approve': 'cascade', 'cross_function': 'cascade',
                 'signed': 'cascade', 'posted': 'cascade', 'cancel': 'cascade'})


    def send_to_check(self):
        for rec in self:
            rec.write({'state': 'check'})

    def check_user_send_to_approve(self):
        for rec in self:
            rec.write({'state': 'to approve'})

    def check_user_cancel(self):
        for rec in self:
            rec.button_cancel()

    def approve_user_send_to_cross_function(self):
        for rec in self:
            rec.write({'state': 'cross_function'})

    def approve_user_cancel(self):
        for rec in self:
            rec.button_cancel()

    def cross_function_user_cancel(self):
        for rec in self:
            rec.button_cancel()


