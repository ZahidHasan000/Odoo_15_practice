from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class ProjectSiteStockPickingI(models.Model):
    _inherit = 'stock.picking'

    project_site_receipt = fields.Many2one('stock.picking', string="Project Sites Receipt ID",
                                           domain="[('picking_type_id.code', '=', 'incoming'), ('location_dest_id.name', '=', 'Project Sites')]")

    @api.onchange('project_site_receipt')
    def receipt_action_delivery(self):
        for rec in self:
            if rec.picking_type_code == 'outgoing':
                if rec.project_site_receipt:
                    rec.location_id = rec.project_site_receipt.location_dest_id.id
                    line_list1 = []
                    for item in rec.project_site_receipt.move_ids_without_package:
                        line_values1 = {
                            'name': item.product_id.name,
                            'product_id': item.product_id.id,
                            'location_id': rec.project_site_receipt.location_dest_id.id,
                            'location_dest_id': rec.location_dest_id.id,
                            'product_uom': item.product_uom.id,
                            'product_uom_qty': item.product_uom_qty,
                        }
                        line_list1.append((0, 0, line_values1))

                    rec.move_ids_without_package = line_list1

                else:
                    rec.move_ids_without_package = False
                    rec.location_id = rec.picking_type_id.default_location_src_id.id
