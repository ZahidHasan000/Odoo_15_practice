# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from dataclasses import field
from email.policy import default

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date, datetime, timedelta

import json
import requests
# from urllib.parse import urlparse
import urllib.parse
from odoo.fields import Command


class LcManagement(models.Model):
    _name = 'lc.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Lc Management'

    name = fields.Char(string='Name', required=True, readonly=True,
                       index=True, default=lambda self: _('New'), tracking=True)
    lc_number = fields.Char(string='LC Number')
    state = fields.Selection([
        ('to_open', 'To Open'),
        ('draft', 'Draft'),
        ('transmitted', 'Transmitted'),
        ('shipped', 'Shipped'),
        ('port', 'Port'),
        ('clearing', 'Clearing'),
        ('grn', 'GRN'),
    ], string='Status', store=True, readonly=True, index=True, copy=False, default='to_open', tracking=True)

    purchase_order = fields.Many2one('purchase.order', string="Purchase Order", required=True, tracking=True)
    supplier = fields.Many2one(related="purchase_order.partner_id", string="Supplier",  tracking=True)
    incoterm = fields.Char(related="purchase_order.incoterm_id.display_name", string="incoterm", tracking=True)
    lc_type = fields.Selection([
        ("at_sight_with_add_confirmation", "At Sight With Add Confirmation"),
        ("deferred", "Deferred"),
    ], related="purchase_order.lc_type", string='LC Type', tracking=True)
    product_type = fields.Selection([
        ("raw_material", "Raw Material"),
        ("capital_machinery", "Capital Machinery"),
    ], related="purchase_order.product_type", string='Product Type', tracking=True)
    port_of_landing = fields.Selection([
        ("chittagong", "Chittagong"),
        ("mongla", "Mongla"),
        ("payra", "Payra"),
        ("shahjalal", "Shahjalal"),
    ], string='Port of Landing', tracking=True)
    shipment_mode = fields.Selection([
        ("sea", "Sea"),
        ("air", "Air"),
        ("courier", "Courier"),
    ], related="purchase_order.shipment_mode", string='Mode of Shipment', tracking=True)
    delivery_time = fields.Char(string="Delivery Time", tracking=True)

    lc_margin = fields.Float(string="LC Margin %", tracking=True)
    insurance = fields.Float(string="Insurance", tracking=True)
    custom_duty = fields.Float(string="Custom Duty", tracking=True)

    country_origin = fields.Char(related="purchase_order.country_of_origin.name", string="Country Origin", tracking=True)
    currency_id = fields.Many2one('res.currency', related="purchase_order.currency_id", string="Currency", tracking=True)
    rate = fields.Float(string="Rate", tracking=True)
    lc_total_value = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        related="purchase_order.amount_total",
        string="LC Total Vlue", tracking=True
    )
    insurance_provider = fields.Many2one('res.partner', string="Insurance Provider", tracking=True)
    port_of_origin = fields.Char(related="purchase_order.port_of_origin", string="Port of Origin", tracking=True)

    issue_bank = fields.Many2one('res.bank', string="Issuing Bank", tracking=True)
    notes = fields.Html(string='Notes', tracking=True)

    discount_on_net_premium = fields.Float(string="Discount on Net Premium", tracking=True)
    insurance_paid = fields.Float(string="Net Premium Paid", tracking=True)
    vat_on_insurance = fields.Float(string="VAT on Insurance", tracking=True)
    stamp_duty = fields.Float(string="Stamp Duty", tracking=True)
    lc_margin_amount = fields.Float(string="LC Margin Amount", tracking=True)
    vat_foreign_trade = fields.Float(string="VAT Foreign Trade", tracking=True)
    vat_on_forex_other = fields.Float(string="VAT on FOREX Other", tracking=True)
    vat_on_lc_comm = fields.Float(string="VAT on LC Comm.", tracking=True)
    comm_forex_others = fields.Float(string="Comm. Forex Others", tracking=True)
    stationery = fields.Float(string="Stationery", tracking=True)
    swift_income = fields.Float(string="Swift Income", tracking=True)
    comm_lc_cash = fields.Float(string="Comm. LC - Cash", tracking=True)
    comm_add_conf = fields.Float(string="Comm. Add Conf.", tracking=True)
    stamps_in_hand = fields.Float(string="Stamps in Hand", tracking=True)
    comm_bdt = fields.Float(string="Comm. BDT", tracking=True)

    lc_confirmation = fields.Selection([
        ("yes", "Yes"),
        ("no", "No"),
    ], string='Confirmation', tracking=True)
    lc_draft_at = fields.Selection([
        ("sight", "Sight"),
        ("90_days", "90 Days"),
        ("120_days", "120 Days"),
        ("180_days", "180 Days"),
        ("360_days", "360 Days"),
    ], string='Draft At', tracking=True)
    lc_draft_from = fields.Selection([
        ("lc_opening", "LC Opening"),
        ("bill_of_landing", "Bill of Landing"),
        ("acceptance", "Acceptance"),
    ], string='Draft From', tracking=True)
    lc_partial_shipment = fields.Selection([
        ("allowed", "Allowed"),
        ("not_allowed", "Not Allowed"),
    ], string='Partial Shipment', tracking=True)
    lc_transhipment = fields.Selection([
        ("allowed", "Allowed"),
        ("not_allowed", "Not Allowed"),
    ], string='Transhipment', tracking=True)
    lc_date_of_issue = fields.Date(string='Date of Issue', tracking=True)
    lc_date_of_expiry = fields.Date(string='Date of Expiry', tracking=True)
    lc_last_date_of_shipment = fields.Date(string='Last Date of Shipment', tracking=True)
    lc_place_of_expiry_1 = fields.Many2one('res.country', string='Place of Expiry', tracking=True)

    lc_insurance_account = fields.Many2one('account.account', string='Insurance Account', tracking=True)
    lc_payment_account = fields.Many2one('account.account', string='Payment Account', tracking=True)
    lc_vat_account = fields.Many2one('account.account', string='VAT Account', tracking=True)
    lc_margin_account = fields.Many2one('account.account', string='LC Margin Account', tracking=True)
    insurance_date = fields.Date(string='Date', tracking=True)
    lc_insurance_journal1 = fields.Many2one('account.move', string='LC Insurance Journal', tracking=True)

    lc_vat_account2 = fields.Many2one('account.account', string='VAT Account', tracking=True)
    lc_payment_account2 = fields.Many2one('account.account', string='Payment Account', tracking=True)
    lc_commission_account = fields.Many2one('account.account', string='Commission Account', tracking=True)
    lc_commission_vat_account = fields.Many2one('account.account', string="Vat Com Account")
    lc_commission_date = fields.Date(string="Date", tracking=True)
    lc_commission_payment_account = fields.Many2one('account.account', string="Commission Pay Account")
    lc_margin_date1 = fields.Date(string="Date", tracking=True)
    lc_margin_journal1 = fields.Many2one('account.move', string="LC Margin Journal", tracking=True)
    lc_commission_journal1 = fields.Many2one('account.move', string="LC Commission Journal", tracking=True)
    lc_vat_journal1 = fields.Many2one('account.move', string="LC VAT Journal", tracking=True)

    lc_3rd_party_bank = fields.Many2one('account.account', string='3rd Party Bank', tracking=True)
    lc_upas_payment_journal = fields.Many2one('account.move', string='Payment Journal', tracking=True)
    lc_upas_vendor_bill = fields.Many2one('account.move', string='Vendor Bill', tracking=True)

    # domain = lambda self: self._get_invoice_ids()
    lc_settlement_margin_amount = fields.Float(string="Margin Amount", tracking=True)
    lc_settlement_loan_amount = fields.Float(string="Loan Amount", tracking=True)
    lc_settlement_from = fields.Many2one('account.account', string="Settlement From", tracking=True)
    lc_settlement_journal_entry = fields.Many2one('account.move', string="Journal Entry", tracking=True)

    lc_deferred_margin_amount = fields.Float(string="Margin Amount", tracking=True)
    lc_deferred_loan_amount = fields.Float(string="Loan Amount", tracking=True)
    lc_deferred_vendor_bill = fields.Many2one('account.move', string='Vendor Bill', tracking=True)
    lc_deferred_from = fields.Many2one('account.account', string="Settlement From", tracking=True)
    lc_deferred_journal_entry = fields.Many2one('account.move', string="Journal Entry", tracking=True)

    lc_shipment_ids = fields.One2many('lc.shipment', 'lc_id', string="Shipment Details", tracking=True)
    shipment_details = fields.Char(string="Shipment", tracking=True)

    payment_upas_shipment_line_ids = fields.One2many('payment.upas.shipment.line', 'lc_id',
                                                     string='Payment UPAS Shipment Line', tracking=True)

    # Different Currency's
    lc_insurance_currency = fields.Many2one('res.currency', string="Insurance Currency")
    lc_margin_currency = fields.Many2one('res.currency', string="Margin Currency")
    lc_vat_currency = fields.Many2one('res.currency', string="VAT Currency")
    lc_commission_currency = fields.Many2one('res.currency', string="Commission Currency")
    # Default Journal
    def get_default_journal(self):
        journal = self.env['account.journal'].sudo().search([('name', '=', 'Import Commercial')])
        return journal.id

    default_journal = fields.Many2one('account.journal', string="Journal")

    @api.onchange('lc_insurance_currency')
    def get_insurance_currency_rate(self):
        if self.lc_insurance_currency:
            company = self.env.company
            today_date = self.insurance_date if self.insurance_date else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.lc_insurance_currency

            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.lc_insurance_currency_rate = final_rate / 100.00
        else:
            self.lc_insurance_currency_rate = 1.00

    @api.onchange('lc_margin_currency')
    def get_margin_currency_rate(self):
        if self.lc_margin_currency:
            company = self.env.company
            today_date = self.lc_margin_date1 if self.lc_margin_date1 else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.lc_margin_currency
            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.lc_margin_currency_rate = final_rate / 100.00
        else:
            self.lc_margin_currency_rate = 1.00

    @api.onchange('lc_vat_currency')
    def get_vat_currency_rate(self):
        if self.lc_vat_currency:
            company = self.env.company
            today_date = self.lc_margin_date1 if self.lc_margin_date1 else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.lc_vat_currency
            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.lc_vat_currency_rate = final_rate / 100.00
        else:
            self.lc_vat_currency_rate = 1.00

    @api.onchange('lc_commission_currency')
    def get_commission_currency_rate(self):
        if self.lc_commission_currency:
            company = self.env.company
            today_date = self.lc_commission_date if self.lc_commission_date else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.lc_commission_currency
            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.lc_commission_currency_rate = final_rate / 100
        else:
            self.lc_commission_currency_rate = 1.00

    # Currency Rate
    lc_insurance_currency_rate = fields.Float(string="Currency Rate BDT", digits=(16, 12))
    lc_margin_currency_rate = fields.Float(string="Currency Rate BDT", digits=(16, 12))
    lc_vat_currency_rate = fields.Float(string="Currency Rate BDT", digits=(16, 12))
    lc_commission_currency_rate = fields.Float(string="Currency Rate BDT", digits=(16, 12))

    shipping_currency = fields.Many2one('res.currency', string="Shipping Currency")

    @api.onchange('shipping_currency')
    def get_shipping_currency_rate(self):
        if self.shipping_currency:
            company = self.env.company
            today_date = fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.shipping_currency
            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.shipping_currency_rate = final_rate / 100.00
        else:
            self.shipping_currency_rate = 1.0000

    shipping_currency_rate = fields.Float(string="Shipping Rate", default=1.0000, digits=(16, 12))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('lc.management') or _('New')
        res = super(LcManagement, self).create(vals)
        # if res.purchase_order.sourcing_type != 'import':
        #     raise UserError(_('This Purchase Order Sourcing Type Local, Please Select Import Type Purchase Order'))
        if vals.get('purchase_order'):
            print('######', res.id)
            res.purchase_order.import_lc = res.id

            res.shipping_currency = res.purchase_order.currency_id.id
            from_currency = self.env.company.currency_id
            to_currency = res.purchase_order.currency_id
            company = self.env.company
            today_date = fields.Date.today()
            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100 / rates
            res.shipping_currency_rate = final_rate / 100

        return res
    
    def write(self, vals):
        res = super(LcManagement, self).write(vals)
        for lc in self:
            if vals.get('purchase_order'):
                lc.purchase_order.import_lc = lc.id
        return res

    def print_move_ids(self):
        if self.purchase_order:
            print('self.get_invoice_ids()')

    @api.depends('purchase_order')
    def _get_invoice_ids(self):
        move_ids = []
        for rec in self:
            print('*******')

    def action_send_draft(self):
        for rec in self:
            rec.create_journal_entry_for_insurance()
        return self.write({'state': 'draft'})

    def action_return_to_open(self):
        return self.write({'state': 'to_open'})

    def go_transmitted(self):
        for rec in self:
            rec.purchase_order.lc_number = rec.lc_number
            rec.lc_margin_vat_commission_journal_created1()
            rec.lc_margin_vat_commission_journal_created2()
            rec.lc_margin_vat_commission_journal_created3()
        return self.write({'state': 'transmitted'})

    def transmitted(self):
        self.create_journal_entry_for_insurance()
        # return self.write({'state': 'transmitted'})

    def go_shipped(self):
        return self.write({'state': 'shipped'})

    def go_port(self):
        return self.write({'state': 'port'})

    def go_clearing(self):
        return self.write({'state': 'clearing'})

    def go_grn(self):
        return self.write({'state': 'grn'})

    #this for create when move it to open to draft
    def create_journal_entry_for_insurance(self):
        for rec in self:
            rec.lc_insurance_journal1 = False
            if not rec.lc_number:
                raise UserError(_('Please Enter a LC Number First!'))
            new_lines = []
            if rec.lc_insurance_account and rec.lc_vat_account and rec.lc_payment_account:
                reference = 'Insurance For ' + rec.lc_number if rec.lc_number else ''
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                print('journal', journal_id)
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.insurance_date,
                    'journal_id': journal_id,
                    'currency_id': rec.env.company.currency_id.id
                })

                if journal:
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_insurance_account.id,
                                'name': 'Net Premium Paid for ' + rec.lc_number if rec.lc_number else '',
                                'move_id': journal.id,
                                'currency_id': rec.lc_insurance_currency.id,
                                "amount_currency": rec.insurance_paid,
                                "debit": rec.insurance_paid * rec.lc_insurance_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_vat_account.id,
                                'name': 'Vat on Insurance for ' + rec.lc_number if rec.lc_number else '',
                                'move_id': journal.id,
                                'currency_id': rec.lc_insurance_currency.id,
                                "amount_currency": rec.vat_on_insurance,
                                "debit": rec.vat_on_insurance * rec.lc_insurance_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_insurance_account.id,
                                'name': 'Stamp Duty for ' + rec.lc_number if rec.lc_number else '',
                                'move_id': journal.id,
                                'currency_id': rec.lc_insurance_currency.id,
                                "amount_currency": rec.stamp_duty,
                                "debit": rec.stamp_duty * rec.lc_insurance_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_payment_account.id,
                                'name': reference,
                                'move_id': journal.id,
                                'currency_id': rec.lc_insurance_currency.id,
                                "amount_currency": (rec.insurance_paid+rec.vat_on_insurance+rec.stamp_duty) * -1,
                                "debit": 0.0,
                                "credit": (rec.insurance_paid+rec.vat_on_insurance+rec.stamp_duty) * rec.lc_insurance_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_insurance_journal1 = journal.id
                    account_item = []
                    for item in journal.line_ids.filtered(lambda line: line.debit > 0):
                        rec.env['landed.cost.item'].sudo().create({
                            'lc_id': rec.id,
                            'account_id': item.account_id.id,
                            'currency_id': journal.currency_id.id,
                            'label': item.name,
                            'landed_cost_amount': item.debit,
                        })

    #LC Margin, VAT and Commission Journal to be created

    @api.onchange('rate', 'lc_margin')
    def calculate_lc_margin_amount1(self):
        for rec in self:
            if rec.rate and rec.lc_margin:
                amount = rec.rate * rec.lc_margin / 100.00 * rec.lc_total_value
                rec['lc_margin_amount'] = amount
            else:
                rec['lc_margin_amount'] = 0.00

    # this 3 for create when move it draft to transmit
    def lc_margin_vat_commission_journal_created1(self):
        for rec in self:
            if rec.lc_margin_account and rec.lc_payment_account2:
                reference = 'LC Margin For LC ' + str(rec.lc_number)
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.lc_margin_date1,
                    'journal_id': journal_id,
                    'currency_id': rec.env.company.currency_id.id
                })

                if journal:
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_margin_account.id,
                                "partner_id": rec.supplier.id,
                                'move_id': journal.id,
                                'name': 'LC Margin For LC ' + rec.lc_number,
                                'currency_id': rec.lc_margin_currency.id,
                                "amount_currency": rec.lc_margin_amount,
                                "debit": rec.lc_margin_amount * rec.lc_margin_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_payment_account2.id,
                                'name': 'LC Margin For LC ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_margin_currency.id,
                                "amount_currency": rec.lc_margin_amount * -1,
                                "debit": 0.0,
                                "credit": rec.lc_margin_amount * rec.lc_margin_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_margin_journal1 = journal.id

                    # for item in journal.line_ids.filtered(lambda line: line.debit > 0):
                    #     rec.env['landed.cost.item'].sudo().create({
                    #         'lc_id': rec.id,
                    #         'account_id': item.account_id.id,
                    #         'currency_id': journal.currency_id.id,
                    #         'label': item.name,
                    #         'landed_cost_amount': item.debit,
                    #     })

    def lc_margin_vat_commission_journal_created2(self):
        for rec in self:
            if rec.lc_commission_account and rec.lc_commission_payment_account:
                reference = 'Commission For LC ' + rec.lc_number
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.lc_commission_date,
                    'journal_id': journal_id,
                    'currency_id':  rec.env.company.currency_id.id
                })

                if journal:
                    commission_credit_amount = rec.stationery + rec.swift_income + rec.comm_lc_cash + \
                                               rec.comm_add_conf + rec.stamps_in_hand + rec.comm_bdt + rec.comm_forex_others + \
                                               rec.vat_on_lc_comm

                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Stationery For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.stationery,
                                "debit": rec.stationery * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Swift Charge For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.swift_income,
                                "debit": rec.swift_income * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Comm. LC-Cash For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.comm_lc_cash,
                                "debit": rec.comm_lc_cash * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Comm. Add Conf. For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.comm_add_conf,
                                "debit": rec.comm_add_conf * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Stamps in Hand For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.stamps_in_hand,
                                "debit": rec.stamps_in_hand * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Comm. BD For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.comm_bdt,
                                "debit": rec.comm_bdt * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_account.id,
                                'name': 'Comm. Forex Others For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.comm_forex_others,
                                "debit": rec.comm_forex_others * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_vat_account.id,
                                'name': 'Vat Commission For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": rec.vat_on_lc_comm,
                                "debit": rec.vat_on_lc_comm * rec.lc_commission_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_commission_payment_account.id,
                                "name": reference,
                                'move_id': journal.id,
                                'currency_id': rec.lc_commission_currency.id,
                                "amount_currency": commission_credit_amount * -1,
                                "debit": 0.0,
                                "credit": commission_credit_amount * rec.lc_commission_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_commission_journal1 = journal.id

                    for item in journal.line_ids.filtered(lambda line: line.debit > 0):
                        rec.env['landed.cost.item'].sudo().create({
                            'lc_id': rec.id,
                            'account_id': item.account_id.id,
                            'currency_id': journal.currency_id.id,
                            'label': item.name,
                            'landed_cost_amount': item.debit,
                        })

    def lc_margin_vat_commission_journal_created3(self):
        for rec in self:
            if rec.lc_vat_account2 and rec.lc_payment_account2:
                reference = 'VAT for LC Margin For ' + rec.lc_number
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.lc_margin_date1,
                    'journal_id': journal_id,
                    'currency_id':  rec.env.company.currency_id.id,
                })

                if journal:
                    vat_for_margin_credit_amount = rec.vat_foreign_trade + rec.vat_on_forex_other
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_vat_account2.id,
                                'name': 'VAT Foreign Trade For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_vat_currency.id,
                                "amount_currency": rec.vat_foreign_trade,
                                "debit": rec.vat_foreign_trade * rec.lc_vat_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_vat_account2.id,
                                'name': 'VAT on FOREX Other For ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_vat_currency.id,
                                "amount_currency": rec.vat_on_forex_other,
                                "debit": rec.vat_on_forex_other * rec.lc_vat_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_payment_account2.id,
                                'name': reference,
                                'move_id': journal.id,
                                'currency_id': rec.lc_vat_currency.id,
                                "amount_currency": vat_for_margin_credit_amount * -1,
                                "debit": 0.0,
                                "credit": vat_for_margin_credit_amount * rec.lc_vat_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_vat_journal1 = journal.id

                    # for item in journal.line_ids.filtered(lambda line: line.debit > 0):
                    #     rec.env['landed.cost.item'].sudo().create({
                    #         'lc_id': rec.id,
                    #         'account_id': item.account_id.id,
                    #         'currency_id': journal.currency_id.id,
                    #         'label': item.name,
                    #         'landed_cost_amount': item.debit,
                    #     })

    def transfer_shipment_in_lc(self, shipment=1):
        for rec in self:
            po_order = rec.env['purchase.order'].sudo().search([['name', '=', 'P00009']])
            if po_order:
                print(len(po_order.order_line)+shipment)

    c_and_f_bill_currency = fields.Many2one('res.currency', string="Bill Currency",
                                            default=lambda self: self.env.company.currency_id)
    c_and_f_vendor = fields.Many2one('res.partner', string="Vendor")
    c_and_f_amount = fields.Float('Amount')
    c_and_f_bill_number = fields.Many2one('account.move', string="C&F Bill")

    def create_c_and_f_bill(self):
        for rec in self:
            if rec.c_and_f_bill_number:
                raise UserError(_("Already a bill has been created !"))

            else:
                product = rec.env['product.product'].sudo().search([('name', '=', 'C&F Charges')], limit=1)
                if not rec.c_and_f_ids:
                    raise UserError(_('NO C&F Item in the list !'))

                else:
                    reference = 'C&F Bill For ' + rec.lc_number
                    journal = rec.env['account.journal'].sudo().search([('code', '=', 'BILL')], limit=1)

                    move = rec.env['account.move'].sudo().create({
                        'move_type': 'in_invoice',
                        'partner_id': rec.c_and_f_vendor.id,
                        'ref': reference,
                        'date': fields.Date.today(),
                        'invoice_date': fields.Date.today(),
                        'journal_id': journal.id,
                        'currency_id': rec.c_and_f_bill_currency.id,
                    })
                    if move:
                        for item in rec.c_and_f_ids:
                            vals = {
                                "invoice_line_ids": [
                                    [0, 0, {
                                        'product_id': item.product_id.id,
                                        'name': reference,
                                        'account_id': item.account_id.id,
                                        'quantity': 1,
                                        'price_unit': item.amount,
                                    }],
                                ]
                            }

                            move.write(vals)

                        move.action_post()
                        rec.c_and_f_bill_number = move.id

                        for item in move.line_ids.filtered(lambda line: line.debit > 0):
                            rec.env['landed.cost.item'].sudo().create({
                                'lc_id': rec.id,
                                'account_id': item.account_id.id,
                                'currency_id': move.currency_id.id,
                                'label': item.name,
                                'landed_cost_amount': item.debit,
                            })

    # LC Amendment
    amendment_date = fields.Date('Date')
    amendment_currency = fields.Many2one('res.currency', string='Currency')
    amendment_currency_rate = fields.Float(string='Currency Rate BDT', default=1.00 , digits=(16, 12))
    lc_amendment_charge = fields.Float(string="LC Amendment Charge")
    lc_amendment_account = fields.Many2one('account.account', string="LC Amendment Account")
    lc_amendment_pay_account = fields.Many2one('account.account', string="Payment Account")
    lc_amendment_journal = fields.Many2one('account.move', string="LC Amendment Journal")

    @api.onchange('amendment_currency')
    def get_amendment_currency_rate(self):
        if self.amendment_currency:
            company = self.env.company
            today_date = self.amendment_date if self.amendment_date else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.amendment_currency

            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.amendment_currency_rate = final_rate / 100.00
        else:
            self.amendment_currency_rate = 1.00

    def create_amendment_journal(self):
        for rec in self:
            if rec.lc_amendment_account and rec.lc_amendment_pay_account and not rec.lc_amendment_journal:
                reference = 'LC Amendment For LC ' + str(rec.lc_number)
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.amendment_date,
                    'journal_id': journal_id,
                    'currency_id': rec.env.company.currency_id.id
                })

                if journal:
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_amendment_account.id,
                                'move_id': journal.id,
                                'name': 'LC Amendment For LC ' + rec.lc_number,
                                'currency_id': rec.amendment_currency.id,
                                "amount_currency": rec.lc_amendment_charge,
                                "debit": rec.lc_amendment_charge * rec.amendment_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_amendment_pay_account.id,
                                'name': 'LC Amendment For LC ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.amendment_currency.id,
                                "amount_currency": rec.lc_amendment_charge * -1,
                                "debit": 0.0,
                                "credit": rec.lc_amendment_charge * rec.amendment_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_amendment_journal = journal.id

                    for item in journal.line_ids.filtered(lambda line: line.debit > 0):
                        rec.env['landed.cost.item'].sudo().create({
                            'lc_id': rec.id,
                            'account_id': item.account_id.id,
                            'currency_id': journal.currency_id.id,
                            'label': item.name,
                            'landed_cost_amount': item.debit,
                        })

    ##
    landed_cost_line = fields.One2many('landed.cost.item', 'lc_id', string="Landed Cost Line")

    def apply_landed_cost(self):
        for rec in self:
            if any(val['locked_item'] == False for val in rec.landed_cost_line):
                landed_cost = rec.env['stock.landed.cost'].sudo().create({
                    'date': fields.Date.today(),
                    'picking_ids': [(6,0, rec.lc_shipment_ids.picking_id.ids)], #rec.lc_shipment_ids.picking_id.ids
                    'target_model': 'picking',
                    'lc_id': rec.id,
                    'lc_number': rec.lc_number,
                    'purchase_order_ids': [(6,0, rec.purchase_order.ids)],
                })
                product = rec.env['product.product'].sudo().search([('name', '=', 'LC Advance Expenses')])
                reference = product.name + ' for: ' + rec.lc_number
                for item in rec.landed_cost_line.filtered(lambda line: not line.locked_item):
                    item.locked_item = True
                    line_item = rec.env['stock.landed.cost.lines'].sudo().search([('cost_id', '=', landed_cost.id),
                                                                                  ('account_id', '=', item.account_id.id)])
                    if line_item:
                        line_item.price_unit += item.landed_cost_amount
                    else:
                        rec.env['stock.landed.cost.lines'].sudo().create({
                            'cost_id': landed_cost.id,
                            'product_id': product.id,
                            'name': reference,
                            'account_id': item.account_id.id,
                            'split_method': 'by_current_cost_price',
                            'currency_id': item.currency_id.id,
                            'price_unit': item.landed_cost_amount,
                        })

                landed_cost.button_validate()
                rec.landed_cost_id = landed_cost.id

                for picking in rec.lc_shipment_ids:
                    transfer = rec.env['stock.picking'].sudo().search([('id', '=', picking.picking_id.id)])
                    if transfer:
                        transfer.landed_cost_id = landed_cost.id
            else:
                raise UserError(_('There are no item to added landed cost'))

    landed_cost_id = fields.Many2one('stock.landed.cost', string="Landed Cost")

# suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n%100 if (n%100)<20 else n%10,"th"))
# print(suf(5))


class PaymentUpasShipment(models.Model):
    _name = 'payment.upas.shipment.line'
    _description = 'Payment UPAS Shipment Line'

    lc_id = fields.Many2one('lc.management', string="LC ID", tracking=True)
    purchase_id = fields.Many2one('purchase.order', related="lc_id.purchase_order", string="Purchase ID", tracking=True)
    settlement_amount = fields.Float(string='Settlement Amount', tracking=True)
    settlement_from = fields.Many2one('account.account', string='Settlement From', tracking=True)
    vendor_bill = fields.Many2one('account.move', string='Vendor Bill', tracking=True)
    payment_journal = fields.Many2one('account.move', string='Payment Journal', tracking=True)
    lc_shipment = fields.Many2one('lc.shipment', string='Shipment', tracking=True)

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.lc_id.payment_upas_shipment_line_ids:
                line_rec.line_no = line_num
                line_num += 1

    line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number', readonly=False, default=False, tracking=True)

    def action_payment(self):
        for rec in self:
            if not rec.settlement_amount:
                raise UserError(_('Please Settlement Account & Save Then Press Payment'))

            if rec.settlement_amount:
                suf = lambda n: "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n % 100 if (n % 100) < 20 else n % 10, "th"))
                ship_sequence = (suf(rec.line_no))

                payment_journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': 'Payment for ' + ship_sequence + ' Shipment - LC ' + rec.lc_id.lc_number,
                    'date': date.today(),
                    'currency_id': rec.env.company.currency_id.id
                })
                if payment_journal:
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.env['account.account'].sudo().search([['name', '=', 'Suppliers Account Payable']], limit=1).id,
                                'partner_id': rec.lc_id.supplier.id,
                                'currency_id': payment_journal.currency_id.id,
                                "debit": rec.settlement_amount,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.settlement_from.id,
                                'currency_id': payment_journal.currency_id.id,
                                "debit": 0.00,
                                "credit": rec.settlement_amount,
                            }]
                        ],
                    }

                    payment_journal.write(vals)
                    payment_journal.action_post()
                    rec.payment_journal = payment_journal.id


class MailInherit(models.Model):
    _inherit = 'mail.tracking.value'

    @api.model
    def _create_tracking_values(self, initial_value, new_value, col_name, col_info, record):
        """ Prepare values to create a mail.tracking.value. It prepares old and
        new value according to the field type.

        :param initial_value: field value before the change, could be text, int,
          date, datetime, ...;
        :param new_value: field value after the change, could be text, int,
          date, datetime, ...;
        :param str col_name: technical field name, column name (e.g. 'user_id);
        :param dict col_info: result of fields_get(col_name);
        :param <record> record: record on which tracking is performed, used for
          related computation e.g. finding currency of monetary fields;

        :return: a dict values valid for 'mail.tracking.value' creation;
        """
        field = self.env['ir.model.fields']._get(record._name, col_name)
        if not field:
            raise ValueError(f'Unknown field {col_name} on model {record._name}')

        values = {'field_id': field.id}

        if col_info['type'] in {'integer', 'float', 'char', 'text', 'datetime'}:
            values.update({
                f'old_value_{col_info["type"]}': initial_value,
                f'new_value_{col_info["type"]}': new_value
            })
        elif col_info['type'] == 'monetary':
            values.update({
                'currency_id': record[col_info['currency_field']].id,
                'old_value_float': initial_value,
                'new_value_float': new_value
            })
        elif col_info['type'] == 'date':
            values.update({
                'old_value_datetime': initial_value and fields.Datetime.to_string(
                    datetime.combine(fields.Date.from_string(initial_value), datetime.min.time())) or False,
                'new_value_datetime': new_value and fields.Datetime.to_string(
                    datetime.combine(fields.Date.from_string(new_value), datetime.min.time())) or False,
            })
        elif col_info['type'] == 'boolean':
            values.update({
                'old_value_integer': initial_value,
                'new_value_integer': new_value
            })
        elif col_info['type'] == 'selection':
            values.update({
                'old_value_char': initial_value and dict(col_info['selection']).get(initial_value, initial_value) or '',
                'new_value_char': new_value and dict(col_info['selection'])[new_value] or ''
            })
        elif col_info['type'] == 'many2one':
            values.update({
                'old_value_integer': initial_value.id if initial_value else 0,
                'new_value_integer': new_value.id if new_value else 0,
                'old_value_char': initial_value.display_name if initial_value else '',
                'new_value_char': new_value.display_name if new_value else ''
            })
        elif col_info['type'] in {'one2many', 'many2many'}:
            values.update({
                'old_value_char': ', '.join(initial_value.mapped('display_name')) if initial_value else '',
                'new_value_char': ', '.join(initial_value.mapped('display_name')) if initial_value else '',
            })
        else:
            raise NotImplementedError(f'Unsupported tracking on field {field.name} (type {col_info["type"]}')

        return values


class LandedCostItem(models.Model):
    _name = 'landed.cost.item'

    name = fields.Char(string="Name")
    locked_item = fields.Boolean(string="Locked")
    lc_id = fields.Many2one('lc.management', string="LC ID")
    account_id = fields.Many2one('account.account', string="Account ID")
    currency_id = fields.Many2one('res.currency', string="Currency")
    label = fields.Char(string="Label")
    landed_cost_amount = fields.Monetary(string="Amount", currency_field="currency_id")


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    lc_id = fields.Many2one('lc.management', string="LC ID")


