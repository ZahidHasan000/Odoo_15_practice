from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    purchase_req_id = fields.Many2one('purchase.request', string="Purchase Request ID")

    @api.onchange('purchase_req_id')
    def get_pr_products_lines(self):
        for rec in self:
            if rec.picking_type_code == 'outgoing':
                print("Somethings else")
                if rec.purchase_req_id:
                    line_list1 = []
                    line_list2 = []
                    for item in rec.purchase_req_id.line_ids:
                        if not item.display_type:
                            line_values1 = {
                                'product_id': item.product_id.id,
                                'description_picking': item.name,
                                'location_id': rec.location_id.id,
                                'location_dest_id': rec.location_dest_id.id,
                                'product_uom_id': item.product_uom_id.id,
                                'product_uom_qty': item.product_qty,
                            }
                            line_list1.append((0, 0, line_values1))

                            line_values2 = {
                                'name': item.name,
                                'product_id': item.product_id.id,
                                'description_picking': item.name,
                                'location_id': rec.location_id.id,
                                'location_dest_id': rec.location_dest_id.id,
                                'product_uom': item.product_uom_id.id,
                                'product_uom_qty': item.product_qty,
                            }
                            line_list2.append((0, 0, line_values2))
                    rec.move_line_ids_without_package = line_list1
                    rec.move_ids_without_package = line_list2

                else:
                    rec.move_line_ids_without_package = False
                    rec.move_ids_without_package = False

    @api.depends('group_id')
    def get_purchase_pr_id(self):
        for rec in self:
            if rec.group_id and rec.picking_type_code == 'incoming':
                purchase = rec.env['purchase.order'].sudo().search([('name', '=', rec.group_id.name)])
                if purchase:
                    rec['purchase_pr_id'] = purchase.purchase_request.id if purchase.purchase_request else False
                else:
                    rec['purchase_pr_id'] = False
            else:
                rec['purchase_pr_id'] = False

    purchase_pr_id = fields.Many2one('purchase.request', compute="get_purchase_pr_id",
                                     string="Purchase Request ID")


# class StockMovePrDescriptions(models.Model):
#     _inherit = 'stock.move'
#
#     pr_description = fields.Text('PR Description')
#
# class