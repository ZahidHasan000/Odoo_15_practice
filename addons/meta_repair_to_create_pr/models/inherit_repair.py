from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class InheritRepair(models.Model):
    _inherit = 'repair.order'

    def create_pr(self):
        for rec in self:
            line_list = []
            for item in rec.operations:
                line_values = {
                    'product_id': item.product_id.id,
                    'name': item.name,
                    'product_qty': item.product_uom_qty,
                    'product_uom_id': item.product_uom.id,
                    'average_cost': item.product_id.standard_price,
                    # 'analytic_account_id': rec.analytic_account_id.id,
                    'estimated_cost': item.product_uom_qty * item.product_id.standard_price,
                }
                line_list.append((0, 0, line_values))

            purchase_request_ctx = dict(
                default_requested_by=self.user_id.id,
                default_repair_id=self.id,
                default_customer_name=self.partner_id.id,
                default_project_number=self.project_number.id,
                default_line_ids=line_list,
            )

            form_view = [(self.env.ref('purchase_request.view_purchase_request_form').id, 'form')]

            return {
                'name': 'Purchase Requests',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request',
                "domain": [('repair_id', '=', self.id)],
                "views": form_view,
                'context': purchase_request_ctx,
            }

    @api.depends('state')
    def _purchase_request_count(self):
        for rec in self:
            if rec.state:
                rec.pr_count = len(
                    self.env['purchase.request'].sudo().search([('repair_id', '=', rec.id)]))

            else:
                rec.pr_count = 0

    pr_count = fields.Integer(compute="_purchase_request_count")

    def view_purchase_request(self):
        self.ensure_one()

        action = {
            'name': _("Purchase Requests"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids
        pr_id = self.env['purchase.request'].sudo().search([('repair_id', '=', self.id)])

        if len(pr_id) == 1:
            order_id = pr_id.id
            action['res_id'] = order_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('purchase_request.view_purchase_request_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', pr_id.ids)]

        return action


class InheritPurchaseRequestRepair(models.Model):
    _inherit = 'purchase.request'

    repair_id = fields.Many2one('repair.order', string="Repair ID")