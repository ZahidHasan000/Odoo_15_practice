
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrderLineInherit, self).create(vals_list)
        if res.order_id.requisition_id or res.order_id.comparison_id:
            res['account_analytic_id'] = res.order_id.customer_reference if res.order_id.customer_reference else False

        return res

    account_analytic_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account',
                                          compute='_compute_account_analytic_id', readonly=False)
