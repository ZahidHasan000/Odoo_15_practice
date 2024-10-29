# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class accAssetCustom(models.Model):
    _inherit = 'account.asset'
    
    ha_acquisition_date = fields.Date(string="Historical Acquisition Date")
    historical_cost = fields.Float(string="Historical Cost")
    ha_depreciation = fields.Float(string="Historical Accumulated Depreciation")
    asset_id = fields.Char('Asset ID')
