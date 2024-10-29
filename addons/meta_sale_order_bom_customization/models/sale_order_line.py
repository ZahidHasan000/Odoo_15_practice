from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class InheritSalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def bom_id_domain(self):
        if self.product_id:
            res = {}
            res['domain'] = {'bom_id': [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)]}
            return res

    bom_id = fields.Many2one('mrp.bom', string="Bill of Materials")

