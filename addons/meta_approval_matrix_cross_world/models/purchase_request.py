
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestInherit(models.Model):
    _inherit = 'purchase.request'

    state = fields.Selection(selection_add=[
        ("draft", "User"),
        ("to_approve",),
        ("checker", "Checker"),
        ("pending_approve", "Waiting for Approve"),
        ("approved",),
        ("rejected",),
        ("done",),
    ], default='draft',
        ondelete={'draft': 'cascade', 'to_approve': 'cascade', 'checker': 'cascade', 'pending_approve': 'cascade',
                  'approved': 'cascade', 'rejected': 'cascade', 'done': 'cascade'})

    def user_send_quotation_to_check(self):
        for rec in self:
            rec.write({'state': 'checker'})

    def checker_send_quotation_to_approval(self):
        for rec in self:
            rec.write({'state': 'pending_approve'})

    def checker_revert_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def checker_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    def approval_approved_pr(self):
        for rec in self:

            for item in rec.line_ids:
                if item.sale_order_line:
                    order_line = self.env['sale.order.line'].sudo().search([('id', '=', item.sale_order_line.id)])
                    order_line.pr_product_total_cost += item.product_qty * item.average_cost
                    # item.sale_order_line.pr_product_total_cost += item.product_qty * item.average_cost

            rec.write({'state': 'approved'})

    def approval_cancel_quotation(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    def approval_revert_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})