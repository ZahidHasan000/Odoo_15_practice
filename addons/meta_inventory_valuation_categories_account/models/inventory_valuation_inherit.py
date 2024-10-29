# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class InventoryValuationInherit(models.Model):
    _inherit = 'stock.valuation.layer'

    product_category = fields.Many2one('product.category', related='product_id.categ_id', string="Category", store=True)
    product_category_valuation_acc = fields.Many2one('account.account', related='product_id.categ_id.property_stock_valuation_account_id',
                                                     string="Stock Valuation Account", store=True)

    @api.depends('product_id')
    def get_valuation_account(self):
        for rec in self:
            if rec.product_id.categ_id.property_stock_valuation_account_id:
                rec['product_category_valuation_acc'] = rec.product_id.categ_id.property_stock_valuation_account_id
            else:
                rec['product_category_valuation_acc'] = False
