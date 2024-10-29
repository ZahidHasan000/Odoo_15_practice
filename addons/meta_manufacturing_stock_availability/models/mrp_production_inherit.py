from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    # def button_mark_done(self):
    #     for rec in self:
    #
    #         if any(item.production_available_loc_qty < item.product_uom_qty for item in rec.move_raw_ids):
    #             raise UserError(_('Component Line Product are not Available in From Location'))
    #
    #         else:
    #             return super().button_mark_done()

    def update_qty(self):
        for rec in self:
            for item in rec.move_raw_ids:
                quant_obj = self.env['stock.quant']
                qty_available = quant_obj._get_available_quantity(item.product_id, item.location_id)
                print('quantity', qty_available)
                item.production_available_loc_qty = qty_available


class StockMoveMrp(models.Model):
    _inherit = 'stock.move'

    @api.depends('product_id', 'location_id')
    def get_location_qty(self):
        for rec in self:
            if rec.product_id and rec.location_id:
                quant_obj = self.env['stock.quant']
                qty_available = quant_obj._get_available_quantity(rec.product_id, rec.location_id)
                print('quantity', qty_available)
                rec['production_available_loc_qty'] = qty_available
            else:
                rec['production_available_loc_qty'] = 0.00

    production_available_loc_qty = fields.Float(compute="get_location_qty", string='Available Qty')

