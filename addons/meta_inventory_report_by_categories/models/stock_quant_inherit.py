from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    @api.depends('product_id')
    def computed_product_category(self):
        for rec in self:
            if rec.product_id:
                rec['categ_id'] = rec.product_id.product_tmpl_id.categ_id.id if rec.product_id.product_tmpl_id.categ_id else False
            else:
                rec['categ_id'] = False

    categ_id = fields.Many2one('product.category', compute='computed_product_category', string="Product Category", store=True)