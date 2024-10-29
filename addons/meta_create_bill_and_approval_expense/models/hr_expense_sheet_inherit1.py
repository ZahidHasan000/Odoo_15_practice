from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class HrExpenseInherit(models.Model):
    _inherit = 'hr.expense'

    expense_for = fields.Many2one('res.partner', string="Expense For")
    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
    ], default='company_account', tracking=True,
        states={'done': [('readonly', True)]},
        string="Paid By")

    exp_seq = fields.Char(string='Expense Sequence', copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals_list):
        if vals_list.get('exp_seq', _('New')) == _('New'):
            vals_list['exp_seq'] = self.env['ir.sequence'].next_by_code('exp.seq.code') or _('New')
        res = super(HrExpenseInherit, self).create(vals_list)
        return res

    def _get_default_expense_sheet_values(self):
        values = super()._get_default_expense_sheet_values()

        values.update({'default_expense_seq': self.exp_seq})

        return values


class HrExpenseSheetInherit1(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection(selection_add=[
        ('draft',),
        ('submit', 'Checker'),
        ('submit_another', 'Approved By'),
        ('approve',),
        ('post',),
        ('done',),
        ('cancel',)
    ], default='draft', ondelete={'draft': 'cascade', 'submit': 'cascade', 'submit_another': 'cascade', 'approve': 'cascade',
                                  'post': 'cascade', 'done': 'cascade', 'cancel': 'cascade'})

    expense_seq = fields.Char(string='Expense Sequence', copy=False, readonly=True, index=True)

    def create_bil_from_expense(self):
        for rec in self:
            line_list = []
            for item in rec.expense_line_ids:
                if item.expense_for:
                    line_values = [(0, 0, {
                        'product_id': item.product_id.id,
                        'analytic_account_id': item.analytic_account_id.id,
                        'quantity': 1,
                        'product_uom_id': item.product_uom_id.id,
                        'price_unit': item.total_amount,
                    })]

                    rec.env['account.move'].create({
                        'partner_id': item.expense_for.id,
                        'move_type': 'in_invoice',
                        'expense_sheet_id': rec.id,
                        'ref': item.exp_seq,
                        'invoice_line_ids': line_values
                    })
                else:
                    raise UserError(_('Please Select The Expense For, in Expense'))

            bills = rec.env['account.move'].sudo().search([('expense_sheet_id', '=', rec.id)])

            action = {
                'name': _("Bills"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'target': 'current',
            }

            if len(bills) == 1:
                bills_id = bills.id
                action['res_id'] = bills_id
                action['view_mode'] = 'form'
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            else:
                action['view_mode'] = 'tree,form'
                action['domain'] = [('id', 'in', bills.ids)]

            return action

    @api.depends('state')
    def _bills_count(self):
        for rec in self:
            if rec.state:
                rec.bill_count = len(
                    self.env['account.move'].sudo().search([('expense_sheet_id', '=', rec.id),
                                                            ('state', '!=', 'cancel')]))

            else:
                rec.bill_count = 0

    bill_count = fields.Integer(compute="_bills_count")

    def view_created_bill(self):
        self.ensure_one()

        action = {
            'name': _("Bills"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'target': 'current',
        }

        account_bill = self.env['account.move'].sudo().search([('expense_sheet_id', '=', self.id),
                                                            ('state', '!=', 'cancel')])

        if len(account_bill) == 1:
            bill_id = account_bill.id
            action['res_id'] = bill_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', account_bill.ids)]

        return action

    def action_unpost(self):
        res = super().action_unpost()
        if self.bill_count > 0:
            self.env['account.move'].sudo().search([('expense_sheet_id', '=', self.id),
                                                                   ('state', '!=', 'cancel')]).button_cancel()
        else:
            pass
        return res

    def action_submit_sheet_another(self):
        self.write({'state': 'submit_another'})

    def _do_approve(self):
        self._check_can_approve()

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['submit_another', 'draft'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'approve', 'user_id': sheet.user_id.id or self.env.user.id})
        notification['params'].update({
            'title': _('The expense reports were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        self.activity_update()
        return notification


class AccountMoveInherit2(models.Model):
    _inherit = 'account.move'

    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense ID")
    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False, default=fields.Date.context_today,
                               states={'draft': [('readonly', False)]})

    def post_all_draft_journal(self):
        # bills = self.env['account.move'].sudo().search([('state', '=', 'draft')])
        # for item in bills:
        self.write({'state': 'cross_function'})

