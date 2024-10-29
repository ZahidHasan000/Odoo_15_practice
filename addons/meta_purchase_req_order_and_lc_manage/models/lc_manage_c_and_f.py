from email.policy import default

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta

import json
import requests
# from urllib.parse import urlparse
import urllib.parse


class LcManageCandF(models.Model):
    _name = 'lc.candf.data'

    product_id = fields.Many2one('product.product', string="Product")
    account_id = fields.Many2one('account.account', string="Account ID")
    amount = fields.Float('Amount')
    lc_manage_id = fields.Many2one('lc.management', string="LC Manage ID")
    not_landed_cost = fields.Boolean('Not Landed Cost', default=False)
    is_landed_cost = fields.Boolean('Not Landed Cost', default=False)

class LCcandfInherit(models.Model):
    _inherit = 'lc.management'

    c_and_f_ids = fields.One2many('lc.candf.data', 'lc_manage_id', string="C&F")
    is_c_and_f_lc = fields.Boolean(string="IS C&F", default=False)


class CandFProduct(models.Model):
    _inherit = 'product.template'

    is_c_and_f_lc = fields.Boolean(string="IS C&F", default=False)

