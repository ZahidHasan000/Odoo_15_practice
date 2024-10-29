from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json
from datetime import date, datetime, timedelta


class ProductAddWizard(models.Model):
    _name = 'product.add.wizard'

    add_date = fields.Date(string="Date", default=fields.Date.context_today)
    requisition_id = fields.Many2one('purchase.requisition', string="Requisition ID")
    item_lines = fields.One2many('product.add.wizard.line', 'add_product_wizard_id', string="Items")

    @api.model
    def default_get(self, fields):
        rec = super(ProductAddWizard, self).default_get(fields)

        tender = self.env['purchase.requisition'].browse(self._context.get('active_ids'))
        print(tender.name)
        if tender:
            line_ids2 = tender.purchase_request.line_ids.filtered(lambda line: line.product_id
                                                                               and line.procurement_qty <= 0.00)
            product_items = [Command.create({
                "pr_line_id": item.id,
                "product_id": item.product_id.id,
                "name": item.name,
                "product_qty": item.product_qty,
                "need_to_procurement_qty": item.product_qty,
                "price_unit": item.average_cost,
                "product_uom_id": item.product_uom_id.id,
            }) for item in line_ids2]

            rec['item_lines'] = product_items

        return rec


    def action_apply(self):
        # print('Done requisition_id')

        print(self.requisition_id.name)
        for rec in self:
            # print(rec.item_lines.mapped("product_id"))

            if any(line.need_to_procurement_qty <= 0.00 for line in rec.item_lines):
                raise UserError(_('Procurement Quantity is zero please enter positive or greater then 0 quantity.'))
            else:
                for item in rec.item_lines:
                    # print(item.product_id.id)
                    item.pr_line_id.procurement_qty += item.need_to_procurement_qty

                    self.env['purchase.requisition.line'].sudo().create({
                        'requisition_id': self.requisition_id.id,
                        'product_id': item.product_id.id,
                        'product_description_variants': item.name,
                        'product_qty': item.need_to_procurement_qty,
                        'demand_qty': item.product_qty,
                        'pr_request_line_id': item.pr_line_id.id,
                        'qty_ordered': 0.00,
                        'product_uom_id': item.product_uom_id.id,
                        'price_unit': item.price_unit,
                    })

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }



class ProductAddWizardLine(models.Model):
    _name = 'product.add.wizard.line'

    add_product_wizard_id = fields.Many2one('product.add.wizard', string="Add Wizi ID")
    pr_line_id = fields.Many2one('purchase.request.line', string="Request Line")
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char('Name')
    product_qty = fields.Float('Demand Quantity')
    need_to_procurement_qty = fields.Float('Need to Procurement Qty')
    price_unit = fields.Float('Price Unit')
    product_uom_id = fields.Many2one("uom.uom", string='Uom')

    @api.onchange('need_to_procurement_qty')
    def check_quantity(self):
        for rec in self:
            need_qty = rec.pr_line_id.product_qty - rec.pr_line_id.procurement_qty
            if rec.need_to_procurement_qty > need_qty:
                rec.need_to_procurement_qty = 0.00
                raise UserError(_('You enter more then the demand qty please check first !'))