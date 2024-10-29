
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'user': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=True,
        states={'user': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'user': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    def _get_default_state(self):
        # state = ''
        for rec in self:
            if rec.opportunity_id:
                state = 'user'

            else:
                state = 'draft'
            return state

    state = fields.Selection(selection_add=[
        ('draft',),
        ('user', 'User'),
        ('engineer', 'Engineering Review'),
        ('check', 'Check'),
        ('to approve', 'Approved'),
        ('cross_function', 'Cross Function'),
        ('mgt_approve', 'MGT'),
        ('sent',),
        ('sale',),
        ('done',),
        ('cancel',),
    ], default='draft', ondelete={'draft': 'cascade', 'user': 'cascade', 'check': 'cascade', 'to approve': 'cascade', 'mgt_approve': 'cascade',
                                 'cross_function': 'cascade', 'sent': 'cascade', 'sale': 'cascade', 'done': 'cascade', 'cancel': 'cascade'})

    def send_to_user(self):
        for rec in self:
            rec.write({'state': 'user'})

    def user_send_quotation_to_engineer(self):
        for rec in self:
            rec.write({'state': 'engineer'})

    def user_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def engineer_send_quotation_to_check(self):
        for rec in self:
            rec.write({'state': 'check'})

    def engineer_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def checker_send_quotation_to_approval(self):
        for rec in self:
            rec.write({'state': 'to approve'})

    def checker_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def approval_send_quotation_to_cross_function(self):
        for rec in self:
            rec.write({'state': 'cross_function'})

    def approval_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def cross_function_send_quotation_to_mgt(self):
        for rec in self:
            rec.write({'state': 'mgt_approve'})

    def cross_function_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def mgt_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'cancel'})

