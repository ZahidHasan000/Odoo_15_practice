# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json


class LocationWiseProductData(models.Model):
    _name = 'location.wise.product.data'

    product_id = fields.Many2one('product.product', string="Product")
    product_uom_id = fields.Many2one('uom.uom', string="UoM")
    product_categ_id = fields.Many2one('product.category', string="Category")
    opening_quantity = fields.Float('Opening Quantity')
    date_range_in_quantity = fields.Float('IN Quantity')
    date_range_out_quantity = fields.Float('Out Quantity')
    closing_quantity = fields.Float('Closing Quantity')


class ProductWiseLocationData(models.Model):
    _name = 'product.wise.location.data'

    location_id = fields.Many2one('stock.location', string="Location")
    product_uom_id = fields.Many2one('uom.uom', string="UoM")
    opening_quantity = fields.Float('Opening Quantity')
    date_range_in_quantity = fields.Float('IN Quantity')
    date_range_out_quantity = fields.Float('Out Quantity')
    closing_quantity = fields.Float('Closing Quantity')


class ProductStockData(models.Model):
    _name = 'product.stock.data'

    product_id = fields.Many2one('product.product', string='Product')
    product_uom = fields.Many2one('uom.uom', string='UoM')
    product_category = fields.Many2one('product.category', string='Category')
    opening_in_qty = fields.Float('Opening in Qty')
    opening_out_qty = fields.Float('Opening out Qty')
    item_line_ids = fields.One2many('product.stock.data.line', 'product_data', string="Items")
    cost_price = fields.Float('Cost')
    sales_price = fields.Float('Sales Price')

    open_final_total = fields.Float('Opn Final Total')
    opn_final_rate = fields.Float('Opn Final rate')
    out_final_total = fields.Float('out Final Total')
    out_final_rate = fields.Float('Out Final rate')


class ProductStockDataLine(models.Model):
    _name = 'product.stock.data.line'
    _order = 'date_time asc'

    date = fields.Date(string="Date")
    date_time = fields.Datetime('Date Time')
    product_data = fields.Many2one('product.stock.data', string="Product Data")
    in_quantity = fields.Float('IN Quantity')
    out_quantity = fields.Float('Out Quantity')
    in_rate = fields.Float('In Rate')
    out_price = fields.Float('Out Price')
    balance = fields.Float('Balance')
    in_value = fields.Float('Out Value')
    out_value = fields.Float('In Value')