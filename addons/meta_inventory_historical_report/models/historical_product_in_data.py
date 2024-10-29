# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json


class HistoricalProductData(models.Model):
    _name = 'location.in.history.data'

    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Datetime(string="Date")
    source_location = fields.Many2one('stock.location', string="Source Location")
    destination_location =fields.Many2one('stock.location', string="Destination Location")
    quantity = fields.Float('Quantity')