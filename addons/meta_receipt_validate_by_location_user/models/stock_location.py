from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    validate_users = fields.Many2many('res.users', string="Validate Users")
