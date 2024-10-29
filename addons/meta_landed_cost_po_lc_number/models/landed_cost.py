from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class LandedCostInherit(models.Model):
    _inherit = 'stock.landed.cost'

    lc_number = fields.Char('LC No')

    @api.depends('picking_ids')
    def get_receipt_type_po(self):
        for rec in self:
            if rec.picking_ids:
                order_id = []
                for item in rec.picking_ids:
                    if item.picking_type_code == 'incoming' and item.group_id:
                        order = rec.env['purchase.order'].sudo().search([('name', '=', item.group_id.name)])
                        order_id.append(order.id)
                po_order = order = rec.env['purchase.order'].sudo().search([('id', '=', order_id)])
                if po_order:
                    rec['purchase_order_ids'] = po_order.ids
                else:
                    rec['purchase_order_ids'] = False

            else:
                rec['purchase_order_ids'] = False

    purchase_order_ids = fields.Many2many('purchase.order', compute="get_receipt_type_po", string="Purchase No")

