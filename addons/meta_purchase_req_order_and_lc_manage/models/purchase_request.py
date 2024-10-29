# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestInherit(models.Model):
    _inherit = 'purchase.request'

    sourcing_type = fields.Selection([
        ("local", "Local"),
        ("import", "Import"),
    ], string='Sourcing Type')
    product_type = fields.Selection([
        ("raw_material", "Raw Material"),
        ("capital_machinery", "Capital Machinery"),
    ], string='Product Type')
    # req_currency_id = fields.Many2one('res.currency', string='Currency')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=False,
                                  default=lambda self: self.env.company.currency_id.id)


class PurchaseRequestLineInherit(models.Model):
    _inherit = 'purchase.request.line'

    unit_price = fields.Float(
        default=0.0,
        string='Unit Price',
    )
    currency_id = fields.Many2one(related="request_id.currency_id", readonly=True)

    @api.onchange('unit_price', 'product_qty')
    def get_estimated_cost(self):
        for rec in self:
            if rec.unit_price > 0.00:
                estimate_cost = rec.unit_price * rec.product_qty
                rec.estimated_cost = estimate_cost
            else:
                rec.estimated_cost = 0.00


