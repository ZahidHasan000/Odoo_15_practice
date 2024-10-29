
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequisitionInherit(models.Model):
    _inherit = "purchase.requisition"

    purchase_request = fields.Many2one('purchase.request', string='Purchase Request',
                                       domain="[('state', 'in', ['approved', 'done'])]")

    # @api.onchange('purchase_request')
    # def get_request_product_line(self):
    #     for rec in self:
    #         product_list = []
    #         if rec.purchase_request:
    #             print('do somethings')
    #             for item in rec.purchase_request.line_ids:
    #                 product_line_values = {
    #                     'product_id': item.product_id.id,
    #                     'product_qty': item.product_qty,
    #                     'product_uom_id': item.product_uom_id.id,
    #                     'account_analytic_id': item.analytic_account_id,
    #                     'price_unit': item.average_cost,
    #                     'price_total': item.product_qty*item.average_cost,
    #                 }
    #                 product_list.append((0, 0, product_line_values))
    #             rec.line_ids = product_list
    #         else:
    #             rec.line_ids = False
    #     print("Success")


class PurchaseRequisitionLineInherit(models.Model):
    _inherit = "purchase.requisition.line"

    @api.onchange('product_id')
    def get_product_cost(self):
        for rec in self:
            if rec.product_id:
                rec['price_unit'] = rec.product_id.product_tmpl_id.standard_price
            else:
                rec['price_unit'] = 0.00

    @api.onchange('product_id', 'product_qty', 'price_unit')
    def get_estimated_price(self):
        for rec in self:
            if rec.product_id or rec.product_qty or rec.price_unit:
                rec['price_total'] = rec.product_qty * rec.price_unit
            else:
                rec['price_total'] = 0.00

    price_total = fields.Float(string='Total')


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    purchase_request = fields.Many2one(related='requisition_id.purchase_request', string='Purchase Request', store=True)
    payment_terms = fields.Char(string='Payment Terms')
    delivery_schedule = fields.Char(string='Delivery Schedule')
    warranty = fields.Char(string='Warranty')

    # @api.model
    # def create(self, vals):
    #     purchase = super(PurchaseOrderInherit, self).create(vals)
    #     if purchase.requisition_id.purchase_request:
    #         purchase.picking_type_id = purchase.requisition_id.purchase_request.picking_type_id.id
    #     return purchase
    #
    # @api.onchange('requisition_id')
    # def get_picking_id(self):
    #     for rec in self:
    #         if rec.requisition_id.purchase_request:
    #             rec.picking_type_id = rec.requisition_id.purchase_request.picking_type_id.id
    #         else:
    #             rec.picking_type_id = False


class DeliverySchedule(models.Model):
    _name = 'delivery.schedule'
    _description = 'Delivery Schedule'

    name = fields.Char(string='Name')


class Warranty(models.Model):
    _name = 'warranty'
    _description = 'Warranty'

    name = fields.Char(string='Name')


