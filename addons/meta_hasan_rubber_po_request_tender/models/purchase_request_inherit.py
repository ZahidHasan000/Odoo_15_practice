
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequestInherit(models.Model):
    _inherit = "purchase.request"

    type_of_expenditure = fields.Selection([
        ('opex', 'OpEx'),
        ('capex', 'CapEx')], string="Type of Expenditure")
    cost_head = fields.Many2one('cost.head', string="Cost Head")
    receipt_location = fields.Many2one('stock.location', string="Receipt Location")
    create_date = fields.Datetime(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Datetime.now,
        tracking=True,
        store=True,
        readonly=True
    )


class PurchaseRequestLineInherit(models.Model):
    _inherit = 'purchase.request.line'

    @api.onchange('product_id')
    def get_product_cost(self):
        for rec in self:
            if rec.product_id:
                rec['average_cost'] = rec.product_id.product_tmpl_id.standard_price
            else:
                rec['average_cost'] = 0.00

    @api.onchange('product_id', 'product_qty', 'average_cost')
    def get_estimated_price(self):
        for rec in self:
            if rec.product_id or rec.product_qty or rec.average_cost:
                rec['estimated_cost'] = rec.product_qty * rec.average_cost
            else:
                rec['estimated_cost'] = 0.00

    average_cost = fields.Float(string='Average Unit Price')

    @api.depends('product_id')
    def get_total_current_stock(self):
        for rec in self:
            if rec.product_id:
                location = rec.env['stock.location'].sudo().search([('id', '=', 8)], limit=1)
                stock_qty = rec.env['stock.quant'].sudo().search([('product_id', '=', rec.product_id.id),
                                                                  ('location_id', '=', location.id)])
                available_quantity = 0.0

                for item in stock_qty:
                    # print('Quantity', item.quantity)
                    available_quantity += item.quantity - item.reserved_quantity

                rec['qty_available'] = available_quantity
            else:
                rec['qty_available'] = 0.00

    qty_available = fields.Float(compute="get_total_current_stock", string="Current Stock")


class CostHead(models.Model):
    _name = 'cost.head'
    _description = 'Cost Head'

    name = fields.Char(string="Name")


