from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class InheritManufactureOrder(models.Model):
    _inherit = 'mrp.production'

    order_id = fields.Many2one('sale.order', string="Sale Order")

    @api.onchange('order_id')
    def bom_product_domain(self):
        products_ids = []
        if self.order_id:
            for item in self.order_id.order_line:
                if item.bom_id:
                    products_ids.append(item.product_id.id)

            res = {}
            res['domain'] = {'product_id': [('id', 'in', products_ids)]}
            return res

