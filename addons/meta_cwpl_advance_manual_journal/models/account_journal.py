# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime


class AccountJournalInherit(models.Model):
    _inherit = 'account.move'

    @api.onchange('employee_id')
    def _compute_dynamic_advance_domain(self):
        for rec in self:
            if rec.employee_id:
                res = {'domain': {'advance_id': [('ea_avbance_for', '=', rec.employee_id.id), ('state', '=', 'approve'), ('remaining_balance', '>', 0.0)]}}

            else:
                res = {'domain': {'advance_id': []}}

        return res

    # @api.onchange('advance_adjustment')
    # def active_adjustment(self):
    #     for rec in self:
    #         if rec.advance_adjustment:
    #             print('#@#@#@#@#@#')
    #         else:
    #             rec.employee_id = False
    #             rec.advance_id = False

    advance_adjustment = fields.Boolean('Advance Adjustment')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    project_id = fields.Many2one('account.analytic.account', string="Project")
    advance_id = fields.Many2one('employee.advance', string="Advance")
    advance_amount = fields.Float('Advance Amount', related="advance_id.ea_amount")
    remaining_balance = fields.Float('Remaining Balance', related="advance_id.remaining_balance")
    adjustment_amount = fields.Float('Adjustment Amount')

    @api.onchange('advance_id', 'advance_adjustment')
    def create_journal_entry(self):
        # for rec in self:
        # rec.line_ids = False
        currency_name = self.env['res.currency'].search([('name', '=', 'BDT')])
        if self.advance_id and self.advance_adjustment:
            self.line_ids = False
            mv_lines = [(0, 0, dict(
                account_id=self.advance_id.ea_account.id,
                partner_id=self.advance_id.ea_avbance_for.address_home_id.id,
                analytic_account_id=self.advance_id.ea_project.id,
                currency_id=currency_name.id,
                name=self.advance_id.ea_description,
                credit=self.remaining_balance,
                debit=0.0,
            ))]

            self.line_ids = mv_lines

        elif self.advance_id and not self.advance_adjustment:
            self.employee_id = False
            self.advance_id = False
            self.line_ids = False

        else:
            pass

    @api.onchange('adjustment_amount')
    def update_credit_amount(self):
        for rec in self:
            if rec.line_ids:
                for item in rec.line_ids.filtered(lambda l: l.credit > 0.0):
                    item.credit = rec.adjustment_amount
                for item2 in rec.line_ids.filtered(lambda l: l.debit > 0.0):
                    item2.debit = rec.adjustment_amount
            else:
                pass

    def action_post(self):
        for rec in self:
            if rec.advance_id:
                amount = 0.0
                for item in rec.line_ids.filtered(lambda l: l.credit > 0.0):
                    amount += item.credit
                rec.advance_id.adjusted_amount += amount
            else:
                pass
        return super().action_post()


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('account_id')
    def get_advance_partner_id(self):
        for rec in self:
            if rec.account_id and rec.move_id.advance_id:
                rec.partner_id = rec.move_id.advance_id.ea_avbance_for.address_home_id.id
            else:
                pass

    @api.depends('move_id')
    def get_all_account_name(self):
        for rec in self:
            name = ''
            if rec.move_id:
                for item in rec.move_id.line_ids:
                    name += str(item.account_id.code) + ' ' + str(item.account_id.name) + ', '
                rec['account_name'] = name
                rec['account_search'] = name
            else:
                rec['account_name'] = name
                rec['account_search'] = name

    account_name = fields.Char('Account', compute='get_all_account_name')
    account_search = fields.Char('Search Account', compute='get_all_account_name', store=True)




 # @api.depends('line_ids')
    # def get_purchase_id(self):
    #     for rec in self:
    #         if rec.move_type == 'in_invoice' and rec.invoice_line_ids:
    #             print('joy1 joy1')
    #             for item in rec.invoice_line_ids[0]:
    #                 print('joy joy', item.name)
    #                 rec['purchase_id_bill'] = item.purchase_order_id.id if item.purchase_order_id else False
    #                 rec['purchase_id_bill2'] = item.purchase_order_id.id if item.purchase_order_id else False
    #             # rec['purchase_id_bill'] = rec.line_ids[0].purchase_order_id.id
    #         else:
    #             rec['purchase_id_bill'] = False
    #             rec['purchase_id_bill2'] = False
    #
    # purchase_id_bill = fields.Many2one('purchase.order', compute="get_purchase_id", string="Purchase")
    # purchase_id_bill2 = fields.Many2one('purchase.order', compute="get_purchase_id", string="Purchase", store=True)