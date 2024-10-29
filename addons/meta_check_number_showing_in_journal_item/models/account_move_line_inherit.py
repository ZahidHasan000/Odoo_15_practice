from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class AccountMoveLineCheckNumber(models.Model):
    _inherit = 'account.move.line'

    check_number = fields.Char(related="move_id.payment_id.payment_check_number", string="Check Number", store=True)
