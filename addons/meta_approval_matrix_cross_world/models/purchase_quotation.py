
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('draft',),
        ('user', 'User'),
        ('check', 'Check'),
        ('cross_function', 'Cross Function'),
        ('approved', 'Approved'),
        ('sent',),
        ('to approve',),
        ('purchase',),
        ('done',),
        ('cancel',),
    ], default='draft', ondelete={ 'draft': 'cascade', 'user': 'cascade', 'check': 'cascade', 'approved': 'cascade', 'cross_function': 'cascade',
                 'sent': 'cascade', 'to approve': 'cascade', 'purchase': 'cascade', 'done': 'cascade', 'cancel': 'cascade'})

    is_locked_order = fields.Boolean(string="Is Locked Order", default=False)

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=Purchase.READONLY_STATES,
                                      required=False, default=False,
                                      help="This will determine operation type of incoming shipment")

    def send_to_user(self):
        for rec in self:
            if rec.picking_type_id:
                rec.write({'state': 'user'})
            else:
                raise UserError(_('You are not select Deliver to Please Select Delivery to First !'))

    def user_send_quotation_to_check(self):
        for rec in self:
            if rec.picking_type_id:
                rec.write({'state': 'check'})
            else:
                raise UserError(_('You are not select Deliver to Please Select Delivery to First !'))

    def user_cancel_po_quotation(self):
        for rec in self:
            rec.button_cancel()

    def checker_send_quotation_to_approved(self):
        for rec in self:
            rec.write({'state': 'cross_function'})

    def checker_cancel_po_quotation(self):
        for rec in self:
            rec.button_cancel()

    def cross_function_sent_to_approve(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def cross_function_cancel_po_quotation(self):
        for rec in self:
            rec.button_cancel()

    def approved_cancel_po_quotation(self):
        for rec in self:
            rec.button_cancel()

    def button_confirm(self):
        for order in self:
            if order.state not in ['approved', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
