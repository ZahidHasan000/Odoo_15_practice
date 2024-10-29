
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta

import json
import requests
# from urllib.parse import urlparse
import urllib.parse


class LcShipment(models.Model):
    _name = 'lc.shipment'
    _description = 'LC Shipment'

    name = fields.Char(string="Name", tracking=True)
    lc_id = fields.Many2one('lc.management', string="LC ID", tracking=True)
    shipment_count = fields.Char(string="Shipment Count", tracking=True)
    picking_id = fields.Many2one('stock.picking', string="Receipt ID", tracking=True)
    shipment_qty = fields.Float(string="Shipment Quantity", tracking=True)
    shipment_date = fields.Date(string='Date', tracking=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s' % (rec.shipment_count)))
        return result

    def open_ui(self):
        if self.picking_id:
            result = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
            # choose the view_mode accordingly

            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = self.picking_id.id

            return result


class LcCandFbill(models.Model):
    _name = 'lc.cf.bill'
    _description = 'LC Bill'

    name = fields.Char(string="Name", tracking=True)
    lc_id = fields.Many2one('lc.management', string="LC ID", tracking=True)
    bill_count = fields.Char(string="Bill Count", tracking=True)
    bill_id = fields.Many2one('account.move', string="Bill ID", tracking=True)
    bill_qty = fields.Float(string="Bill Quantity", tracking=True)
    bill_date = fields.Date(string='Date', tracking=True)


