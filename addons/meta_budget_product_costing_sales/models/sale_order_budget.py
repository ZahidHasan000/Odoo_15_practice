
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderBudget(models.Model):
    _inherit = 'sale.order'

    taf_amount = fields.Float('TAF Amount')

    def budget_product_costing(self):
        for rec in self:
            action = {
                'name': _("Product Costing"),
                'type': 'ir.actions.act_window',
                'res_model': 'product.costing',
                'target': 'current',
            }
            search_costing = self.env['product.costing'].sudo().search([('sale_id', '=', rec.id)])

            if len(search_costing) > 1:
                action['view_mode'] = 'tree,form'
                action['domain'] = [('id', 'in', search_costing.ids)]

            elif len(search_costing) == 1:
                costing_id = search_costing.id
                action['res_id'] = costing_id
                action['view_mode'] = 'form'
                action['views'] = [(self.env.ref('meta_budget_product_costing_sales.view_product_costing_form').id, 'form')]

            else:
                line_list1 = []
                line_list2 = []
                for item1 in rec.order_line.filtered(lambda line: not line.is_downpayment):
                    print('JOyanto')
                    line_values1 = {
                        'display_type': item1.display_type if item1.display_type else False,
                        'order_line': item1.id,
                        'product_id': item1.product_id.id,
                        'name': item1.name,
                        'foreign_currency_subtotal': item1.price_subtotal if rec.pricelist_id.currency_id != rec.company_id.currency_id else 0.00,
                        'currency_rate': 0.00,
                        'product_sales_bdt': item1.price_subtotal if rec.pricelist_id.currency_id == rec.company_id.currency_id else 0.00,
                    }
                    line_list1.append((0, 0, line_values1))

                    line_values2 = {
                        'display_type': item1.display_type if item1.display_type else False,
                        'order_line': item1.id,
                        'product_id': item1.product_id.id,
                        'name': item1.name,
                        'product_cost_bdt': item1.product_id.standard_price * item1.product_uom_qty,
                    }
                    line_list2.append((0, 0, line_values2))
                # print(line_list2)
                line_list3 = [
                    (0, 0, {'name': 'Freight Cost',
                            'product_cost_bdt': 0.0}),
                    (0, 0, {'name': 'Insurance Cost',
                            'product_cost_bdt': 0.0}),
                    (0, 0, {'name': 'Custom Duty',
                            'product_cost_bdt': 0.0}),
                    (0, 0, {'name': 'C&F Cost',
                            'product_cost_bdt': 0.0}),
                    (0, 0, {'name': 'LC Cost',
                            'product_cost_bdt': 0.0}),
                ]

                costing = rec.env['product.costing'].create({
                    'name': 'Budget Costing'+'/'+rec.name,
                    'pricelist_id': rec.pricelist_id.id,
                    'sale_id': rec.id,
                    'taf_amount': rec.taf_amount,
                    'sale_line_ids': line_list1,
                    'costing_product_ids': line_list2,
                    'extra_cost_ids': line_list3,
                })

                costing_id = costing.id
                action['res_id'] = costing_id
                action['view_mode'] = 'form'
                action['views'] = [(self.env.ref('meta_budget_product_costing_sales.view_product_costing_form').id, 'form')]

            return action

    @api.depends('state')
    def _costing_count(self):
        for rec in self:
            if rec.state:
                rec.costing_count = len(
                    self.env['product.costing'].sudo().search([('sale_id', '=', rec.id)]))

            else:
                rec.costing_count = 0

    costing_count = fields.Integer(compute="_costing_count")


class SaleOrderLineBudget(models.Model):
    _inherit = 'sale.order.line'

    pr_product_total_cost = fields.Float('PR Cost')

    # @api.depends('price_subtotal')
    # def foreign_currency_get(self):
    #     for rec in self:
    #         if rec.price_subtotal > 0.0:
    #             rec.foreign_currency_subtotal = rec.price_subtotal
    #         else:
    #             rec.foreign_currency_subtotal = 0.00
    #
    # pricelist_currency = fields.Many2one('res.currency', related='order_id.pricelist_id.currency_id', string="Pricelist Currency")
    # foreign_currency_subtotal = fields.Monetary('Foreign Currency (Subtotal)', compute='foreign_currency_get')
    # currency_rate = fields.Float('Currency Rate')
    # product_sales_bdt = fields.Float('Product Sales in BDT')

    # @api.onchange('')


