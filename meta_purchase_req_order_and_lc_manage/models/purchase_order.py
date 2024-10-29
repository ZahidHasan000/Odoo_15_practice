# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    country_of_origin = fields.Many2one('res.country', string='Country Of Origin', tracking=True)
    lc_type = fields.Selection([
        ("at_sight_with_add_confirmation", "At Sight With Add Confirmation"),
        ("deferred", "Deferred"),
        ("upas", "UPAS"),
    ], string='LC Type', store=True, tracking=True)
    shipment_mode = fields.Selection([
        ("sea", "Sea"),
        ("air", "Air"),
        ("courier", "Courier"),
    ], string='Shipment Mode', store=True, tracking=True)
    port_of_origin = fields.Char(string="Port Of Origin", tracking=True)
    purchase_request = fields.Many2one('purchase.request', string='Purchase Request', store=True, tracking=True)
    sourcing_type = fields.Selection([
        ("local", "Local"),
        ("import", "Import"),
    ], related="purchase_request.sourcing_type", string='Sourcing Type', store=True,
        tracking=True)  # related="purchase_request.sourcing_type",
    product_type = fields.Selection([
        ("raw_material", "Raw Material"),
        ("capital_machinery", "Capital Machinery"),
    ], related="purchase_request.product_type", string='Product Type', store=True,
        tracking=True)  # related="purchase_request.product_type",

    delivery_time = fields.Char(string="Delivery Time", tracking=True)

    import_lc = fields.Many2one('lc.management', string='Import LC', tracking=True)
    lc_status = fields.Selection([
        ('draft', 'Draft'),
        ('transmitted', 'Transmitted'),
        ('shipped', 'Shipped'),
        ('port', 'Port'),
        ('clearing', 'Clearing'),
        ('grn', 'GRN'),
    ], related="import_lc.state", string='LC Status', store=True, tracking=True)
    lc_number = fields.Char(string="LC Number", tracking=True)

    def button_confirm(self):
        if self.sourcing_type == 'import':
            self.create_lc_management()
        return super(PurchaseOrderInherit, self).button_confirm()

    def create_lc_management(self):
        for rec in self:
            journal = self.env['account.journal'].sudo().search([('name', '=', 'Import Commercial')])
            lc = rec.env['lc.management'].sudo().create({
                'purchase_order': rec.id,
                'delivery_time': rec.delivery_time,
                'default_journal': journal.id if journal else False,
            })

            products = rec.env['product.product'].sudo().search([('is_c_and_f_lc', '=', True)])
            for item in products:
                rec.env['lc.candf.data'].sudo().create({
                    'lc_manage_id': lc.id,
                    'product_id': item.id,
                    'account_id': item.property_account_expense_id.id if item.property_account_expense_id else False,
                    'amount': 0.00,
                })

            for item in rec.order_line.filtered(lambda line: line.product_id.name == 'Import Freight'):
                company_currency = rec.env.company.currency_id
                company = rec.env.company
                today_date = fields.Date.today()
                currency_rate = 1
                if item.currency_id != company_currency:
                    rates = self.env['res.currency']._get_conversion_rate(company_currency, item.currency_id, company,
                                                                          today_date)
                    final_rate = 100.00 / rates
                    final_rate2 = final_rate / 100.00
                    currency_rate = final_rate2

                rec.env['landed.cost.item'].sudo().create({
                    'lc_id': lc.id,
                    'account_id': item.product_id.property_account_expense_id.id if item.product_id.property_account_expense_id else False,
                    'currency_id': company_currency.id,
                    'label': item.name,
                    'landed_cost_amount': item.price_unit * currency_rate,
                })

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['purchase_order'] = self.id
        return invoice_vals

    def button_cancel(self):
        res = super().button_cancel()
        for rec in self:
            lc = rec.env['lc.management'].sudo().search([['purchase_order', '=', rec.id]])
            for item in lc:
                item.unlink()
        return res


class LcShipmentCount(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        res = super(LcShipmentCount, self)._action_done()
        for rec in self:
            rec.transfer_shipment_in_lc()
        return res

    def transfer_shipment_in_lc(self, shipment=1):
        for rec in self:
            po_order = rec.env['purchase.order'].sudo().search([['name', '=', rec.origin]])
            if po_order.import_lc:
                shipment_count = len(po_order.import_lc.lc_shipment_ids)
                suf = lambda n: "%d%s" % (
                n, {1: "st", 2: "nd", 3: "rd"}.get(n % 100 if (n % 100) < 20 else n % 10, "th"))
                ship_sequence = (suf(shipment_count + shipment))
                lc = rec.env['lc.management'].sudo().search([['id', '=', po_order.import_lc.id]])
                if lc:
                    vals = {
                        "shipment_details": ship_sequence + ' Shipment',
                        "lc_shipment_ids": [
                            [0, 0, {
                                'shipment_count': ship_sequence + ' Shipment',
                                'picking_id': rec.id,
                                'shipment_date': date.today(),
                            }],
                        ],
                    }

                    lc.write(vals)

    def action_cancel(self):
        res = super().action_cancel()
        for rec in self:
            shipment = rec.env['lc.shipment'].sudo().search([['picking_id', '=', rec.id]])
            for item in shipment:
                item.unlink()
        return res

    landed_cost_id = fields.Many2one('stock.landed.cost', string="Landed Cost")


class AccountMovePurchase(models.Model):
    _inherit = 'account.move'

    purchase_order = fields.Many2one('purchase.order', stiring="Purchase Order", tracking=True)

# suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n%100 if (n%100)<20 else n%10,"th"))
# print(suf(5))

