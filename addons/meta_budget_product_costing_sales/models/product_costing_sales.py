
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductCostingSales(models.Model):
    _name = 'product.costing'
    _description = "Product Costing Sales"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Name')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', depends=["company_id"], store=True, ondelete="restrict")
    sale_id = fields.Many2one('sale.order', string="Sales ID", readonly=1)
    target_cm = fields.Float('Target CM%', default=15)
    actual_cm = fields.Float('Actual CM%', default=10)
    cost_note = fields.Text(string="Note")

    sale_line_ids = fields.One2many('costing.sale.line', 'costing_id', string="Sale Line")
    costing_product_ids = fields.One2many('costing.product.line', 'costing_id', string="Product Costing")
    extra_cost_ids = fields.One2many('extra.cost.line', 'costing_id', string="Extra Costing")
    grant_total_cost_line_ids = fields.One2many('grand.total.cost.line', 'costing_id', string="Grand Total Cost")

    @api.depends('sale_line_ids')
    def sale_line_total(self):
        for rec in self:
            if rec.sale_line_ids:
                rec['total_sales_value'] = sum(item.product_sales_bdt for item in rec.sale_line_ids)
            else:
                rec['total_sales_value'] = 0.00

    @api.depends('sale_id')
    def compute_total_pr_cost(self):
        for rec in self:
            total_cost = []
            line_id = []
            for so in rec.sale_id.order_line.filtered(lambda l: not l.display_type):
                line_id.append(so.id)
            print(line_id)
            request = rec.env['purchase.request'].sudo().search([('order_item', '=', rec.sale_id.id)])
            request_line = rec.env['purchase.request.line'].sudo().search([('sale_order_line', 'in', line_id)])
            # for item in request_line.filtered(lambda prl: prl.sale_order_line in line_id and prl.request_id == request.id):
            for item in request_line:
                print('pr pr', item.request_id.name)
                total_cost.append(item.product_qty * item.average_cost)
            total_amount = sum(total_cost)
            print('amount amount', total_amount)
            if total_amount > 0.00:
                rec['pr_total_cost'] = total_amount
            else:
                rec['pr_total_cost'] = 0.00

    total_sales_value = fields.Float('Total Sales Value', compute='sale_line_total')
    pr_total_cost = fields.Float('PR Product Total Cost', compute="compute_total_pr_cost")

    # Total COST
    taf = fields.Char(string='TAF', default='.')
    warranty = fields.Float('Warranty%', default=0.50)
    contingency = fields.Float('Contingency%', default=1)
    vat = fields.Float('VAT%', default=5)
    tax = fields.Float('TAX%', default=2)

    taf_amount = fields.Float(string='TAF Amount') #related="sale_id.taf_amount",
    warranty_amount = fields.Float('Warranty Amount', default=0.50)
    contingency_amount = fields.Float('Contingency Amount', default=1)
    vat_amount = fields.Float('VAT Amount', default=5)
    tax_amount = fields.Float('TAX Amount', default=2)

    show_grand_total = fields.Boolean('Show Grand Total', default=False)

    def action_grand_total_cost(self):
        self.grant_total_cost_line_ids = [(5, 0, 0)]
        sum_product_cost_bd = sum(item.product_cost_bdt for item in self.costing_product_ids) + sum(item.product_cost_bdt for item in self.extra_cost_ids)
        sum_manual_cost_bd = sum(item.manual_cost_bdt for item in self.costing_product_ids) + sum(item.product_cost_bdt for item in self.extra_cost_ids)
        sum_product_assembly_cost = sum(item.assembly_material for item in self.costing_product_ids) + sum(item.assembly_material for item in self.extra_cost_ids)
        sum_product_inst_material = sum(item.installation_material for item in self.costing_product_ids) + sum(item.installation_material for item in self.extra_cost_ids)
        sum_product_service_material = sum(item.service_material for item in self.costing_product_ids) + sum(item.service_material for item in self.extra_cost_ids)
        sum_product_grand_total = sum(item.grand_total for item in self.costing_product_ids) + sum(item.grand_total for item in self.extra_cost_ids)

        line_values = [(0, 0, {
            'name': 'Grand Total Cost',
            'product_cost_bdt': sum_product_cost_bd,
            'manual_cost_bdt': sum_manual_cost_bd,
            'assembly_material': sum_product_assembly_cost,
            'installation_material': sum_product_inst_material,
            'service_material': sum_product_service_material,
            'grand_total': sum_product_grand_total,
        })]
        self.grant_total_cost_line_ids = line_values
        self.show_grand_total = True

        taf_amnt = self.taf_amount
        warranty_amnt = (self.total_sales_value * self.warranty) / 100 if self.total_sales_value > 0.0 else 0.00
        contingency_amnt = (self.total_sales_value * self.contingency) / 100 if self.total_sales_value > 0.0 else 0.00
        vat_amnt = (self.total_sales_value * self.vat) / 100 if self.total_sales_value > 0.0 else 0.00
        tax_amnt = (self.total_sales_value * self.tax) / 100 if self.total_sales_value > 0.0 else 0.00

        self.warranty_amount = warranty_amnt
        self.contingency_amount = contingency_amnt
        self.vat_amount = vat_amnt
        self.tax_amount = tax_amnt

        self.total_other_cost = taf_amnt + warranty_amnt + contingency_amnt + vat_amnt + tax_amnt
        self.total_sales_cost = (taf_amnt + warranty_amnt + contingency_amnt + vat_amnt + tax_amnt) + sum(item.grand_total for item in self.grant_total_cost_line_ids)
        self.budget_cm = ((self.total_sales_value - self.total_sales_cost) / self.total_sales_value * 100)


    @api.onchange('sale_line_ids', 'warranty', 'contingency', 'vat', 'tax', 'taf_amount')
    def _change_values1(self):
        for rec in self:
            taf_amnt = self.taf_amount if self.taf_amount > 0.0 else 0.0
            warranty_amnt = (rec.total_sales_value * rec.warranty) / 100 if rec.total_sales_value > 0.0 else 0.00
            contingency_amnt = (rec.total_sales_value * rec.contingency) / 100 if rec.total_sales_value > 0.0 else 0.00
            vat_amnt = (rec.total_sales_value * rec.vat) / 100 if rec.total_sales_value > 0.0 else 0.00
            tax_amnt = (rec.total_sales_value * rec.tax) / 100 if rec.total_sales_value > 0.0 else 0.00

            self.warranty_amount = warranty_amnt
            self.contingency_amount = contingency_amnt
            self.vat_amount = vat_amnt
            self.tax_amount = tax_amnt

            # self.total_other_cost = taf_amnt + warranty_amnt + contingency_amnt + vat_amnt + tax_amnt
            # self.total_sales_cost = (taf_amnt + warranty_amnt + contingency_amnt + vat_amnt + tax_amnt) + sum(item.grand_total for item in self.grant_total_cost_line_ids)
            # self.budget_cm = ((self.total_sales_value - self.total_sales_cost) / self.total_sales_value * 100)

    @api.depends('sale_line_ids', 'costing_product_ids', 'extra_cost_ids', 'grant_total_cost_line_ids', 'taf_amount', 'warranty_amount', 'contingency_amount', 'vat_amount', 'tax_amount')
    def all_accountable_summation(self):
        for rec in self:
            rec.total_other_cost = rec.taf_amount + rec.warranty_amount + rec.contingency_amount + rec.vat_amount + rec.tax_amount
            rec.total_sales_cost = (rec.taf_amount + rec.warranty_amount + rec.contingency_amount + rec.vat_amount + rec.tax_amount) + sum(
                item.grand_total for item in rec.grant_total_cost_line_ids) if rec.grant_total_cost_line_ids else 0.00
            total_sales_values = sum(item.product_sales_bdt for item in rec.sale_line_ids) if rec.sale_line_ids else 0.00
            rec.budget_cm = ((total_sales_values - rec.total_sales_cost) / total_sales_values * 100) if total_sales_values > 0.0 else 0.00

    total_other_cost = fields.Float(compute='all_accountable_summation', string='Total Other Cost')
    total_sales_cost = fields.Float(compute='all_accountable_summation', string='Total Sales Cost')
    budget_cm = fields.Float(compute='all_accountable_summation', string='Initial Projected CM%', default=11)

    def update_costing_value(self):
        self.update1()
        self.update2()
        self.update3()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def update1(self):
        for rec in self:
            for item in rec.sale_id.order_line.filtered(lambda line: not line.is_downpayment):
                costing_sale_line = rec.env['costing.sale.line'].sudo().search([('costing_id', '=', rec.id),
                                                                                ('order_line', '=', item.id)])
                if costing_sale_line:
                    total = item.price_subtotal if rec.sale_id.pricelist_id.currency_id == rec.sale_id.company_id.currency_id else 0.00

                    costing_sale_line.product_id = item.product_id.id
                    costing_sale_line.name = item.name
                    costing_sale_line.foreign_currency_subtotal = item.price_subtotal if rec.sale_id.pricelist_id.currency_id != rec.sale_id.company_id.currency_id else 0.00
                    costing_sale_line.product_sales_bdt = total * costing_sale_line.currency_rate if costing_sale_line.currency_rate > 0.00 else total

                else:
                    rec.write({'sale_line_ids': [
                        (0, 0, {
                        'display_type': item.display_type if item.display_type else False,
                        'order_line': item.id,
                        'product_id': item.product_id.id,
                        'name': item.name,
                        'foreign_currency_subtotal': item.price_subtotal if rec.sale_id.pricelist_id.currency_id != rec.sale_id.company_id.currency_id else 0.00,
                        'currency_rate': 0.00,
                        'product_sales_bdt': item.price_subtotal if rec.sale_id.pricelist_id.currency_id == rec.sale_id.company_id.currency_id else 0.00,
                        })
                    ]})

    def update2(self):
        for rec in self:
            for item in rec.sale_id.order_line.filtered(lambda line: not line.is_downpayment):
                costing_product_line = rec.env['costing.product.line'].sudo().search([('costing_id', '=', rec.id),
                                                                                ('order_line', '=', item.id)])
                if costing_product_line:
                    costing_product_line.product_id = item.product_id.id
                    costing_product_line.name = item.name
                    costing_product_line.product_cost_bdt = item.product_id.standard_price * item.product_uom_qty

                else:
                    rec.write({'costing_product_ids': [
                        (0, 0, {
                        'display_type': item.display_type if item.display_type else False,
                        'order_line': item.id,
                        'product_id': item.product_id.id,
                        'name': item.name,
                        'product_cost_bdt': item.product_id.standard_price * item.product_uom_qty,
                        })
                    ]})

    def update3(self):
        for rec in self:
            for item in rec.sale_id.order_line:
                purchase_request_line = rec.env['purchase.request.line'].sudo().search([('sale_order_line', '=', item.id)])
                total = []
                for item2 in purchase_request_line:
                    total.append(item2.product_qty * item2.average_cost)
                    # purchase_request_line.sale_order_line.pr_product_total_cost += item.product_qty * item.average_cost
                item.pr_product_total_cost = sum(total)

    def delete_extra_line(self):
        product = self.env['product.product'].sudo().search([('name', '=', 'Advance from Customer')], limit=1)
        costing_sale_line = self.env['costing.sale.line'].sudo().search([('product_id', '=', product.id)])
        costing_product_line = self.env['costing.product.line'].sudo().search([('product_id', '=', product.id)])
        for line1 in costing_sale_line:
            line1.unlink()
        for line2 in costing_product_line:
            line2.unlink()


class CostingSalesLine(models.Model):
    _name = 'costing.sale.line'

    name = fields.Char(string='Description')
    product_id = fields.Many2one('product.product', string='Product')
    costing_id = fields.Many2one('product.costing', string='Costing ID')
    order_line = fields.Many2one('sale.order.line', string='Order Line')
    pr_product_total_cost = fields.Float(related="order_line.pr_product_total_cost", string='Cost in PR')
    pricelist_currency = fields.Many2one('res.currency', related='costing_id.pricelist_id.currency_id', string="Pricelist Currency")
    foreign_currency_subtotal = fields.Monetary(currency_field='pricelist_currency', string='Foreign Currency (Subtotal)')
    currency_rate = fields.Float('Currency Rate')
    product_sales_bdt = fields.Float('Product Sales in BDT')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.onchange('currency_rate')
    def foreign_rate_in_bdt(self):
        for rec in self:
            if rec.currency_rate > 0:
                rec.product_sales_bdt = rec.foreign_currency_subtotal * rec.currency_rate
            else:
                rec.product_sales_bdt = 0.00


class CostingProductLine(models.Model):
    _name = 'costing.product.line'

    name = fields.Char(string='Description')
    product_id = fields.Many2one('product.product', string='Product')
    costing_id = fields.Many2one('product.costing', string='Costing ID')
    order_line = fields.Many2one('sale.order.line', string='Order Line')
    pr_product_total_cost = fields.Float(related="order_line.pr_product_total_cost", string='Cost in PR')
    pricelist_currency = fields.Many2one('res.currency', related='costing_id.pricelist_id.currency_id', string="Pricelist Currency")
    product_cost_bdt = fields.Float(string='Product Cost in BDT')
    manual_cost_bdt = fields.Float(string='Manual Cost in BDT')
    assembly_material = fields.Float('Assembly Material')
    installation_material = fields.Float('Installation Material')
    service_material = fields.Float('Service Material')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('manual_cost_bdt', 'assembly_material', 'installation_material', 'service_material')
    def _get_grand_total(self):
        for rec in self:
            if rec.manual_cost_bdt > 0.0 or rec.assembly_material > 0.0 or rec.installation_material > 0.0 or rec.service_material > 0.0:
                product_cost = rec.manual_cost_bdt
                assembly_cost = rec.assembly_material
                installation_cost = rec.installation_material
                service_cost = rec.service_material
                rec['grand_total'] = product_cost + assembly_cost + installation_cost + service_cost
            else:
                rec['grand_total'] = 0.0

    grand_total = fields.Float('Grand Total', compute='_get_grand_total')


class ExtraCostLine(models.Model):
    _name = 'extra.cost.line'

    name = fields.Char('Extra Cost')
    costing_id = fields.Many2one('product.costing', string='Costing ID')
    pricelist_currency = fields.Many2one('res.currency', related='costing_id.pricelist_id.currency_id', string="Pricelist Currency")
    product_cost_bdt = fields.Float(string='Product Cost in BDT')
    assembly_material = fields.Float('Assembly Material')
    installation_material = fields.Float('Installation Material')
    service_material = fields.Float('Service Material')
    grand_total = fields.Float('Grand Total')

    @api.onchange('product_cost_bdt', 'assembly_material', 'installation_material', 'service_material')
    def _get_grand_total(self):
        for rec in self:
            if rec.product_cost_bdt > 0.0 or rec.assembly_material > 0.0 or rec.installation_material > 0.0 or rec.service_material > 0.0:
                product_cost = rec.product_cost_bdt
                assembly_cost = rec.assembly_material
                installation_cost = rec.installation_material
                service_cost = rec.service_material
                rec.grand_total = product_cost + assembly_cost + installation_cost + service_cost
            else:
                rec.grand_total = 0.0


class GrandTotalCostLine(models.Model):
    _name = 'grand.total.cost.line'

    name = fields.Char('Grand Cost')
    costing_id = fields.Many2one('product.costing', string='Costing ID')
    pricelist_currency = fields.Many2one('res.currency', related='costing_id.pricelist_id.currency_id', string="Pricelist Currency")

    @api.depends('costing_id.costing_product_ids', 'costing_id.extra_cost_ids')
    def compute_all_costing(self):
        for rec in self:
            print("++++++******++++++")
            sum_product_cost_bd = sum(item1.product_cost_bdt for item1 in rec.costing_id.costing_product_ids) + sum(
                item2.product_cost_bdt for item2 in rec.costing_id.extra_cost_ids) if rec.costing_id.extra_cost_ids and rec.costing_id.costing_product_ids else 0.00

            sum_manual_cost_bd = sum(item11.manual_cost_bdt for item11 in rec.costing_id.costing_product_ids) + sum(
                item12.product_cost_bdt for item12 in rec.costing_id.extra_cost_ids) if rec.costing_id.extra_cost_ids and rec.costing_id.costing_product_ids else 0.00

            sum_product_assembly_cost = sum(item3.assembly_material for item3 in rec.costing_id.costing_product_ids) + sum(
                item4.assembly_material for item4 in rec.costing_id.extra_cost_ids) if rec.costing_id.extra_cost_ids and rec.costing_id.costing_product_ids else 0.00

            sum_product_inst_material = sum(item5.installation_material for item5 in rec.costing_id.costing_product_ids) + sum(
                item6.installation_material for item6 in rec.costing_id.extra_cost_ids) if rec.costing_id.extra_cost_ids and rec.costing_id.costing_product_ids else 0.00

            sum_product_service_material = sum(item7.service_material for item7 in rec.costing_id.costing_product_ids) + sum(
                item8.service_material for item8 in rec.costing_id.extra_cost_ids) if rec.costing_id.extra_cost_ids and rec.costing_id.costing_product_ids else 0.00

            sum_product_grand_total = sum(item9.grand_total for item9 in rec.costing_id.costing_product_ids) + sum(
                item10.grand_total for item10 in rec.costing_id.extra_cost_ids) if rec.costing_id.extra_cost_ids and rec.costing_id.costing_product_ids else 0.00

            rec.product_cost_bdt = sum_product_cost_bd
            rec.manual_cost_bdt = sum_manual_cost_bd
            rec.assembly_material = sum_product_assembly_cost
            rec.installation_material = sum_product_inst_material
            rec.service_material = sum_product_service_material
            rec.grand_total = sum_product_grand_total
            # print(sum(item10.grand_total for item10 in rec.costing_id.extra_cost_ids))
            print(sum_product_grand_total)

    product_cost_bdt = fields.Float(compute='compute_all_costing', string='Product Cost in BDT')
    manual_cost_bdt = fields.Float(compute='compute_all_costing', string='Manual Cost in BDT')
    assembly_material = fields.Float(compute='compute_all_costing', string='Assembly Material')
    installation_material = fields.Float(compute='compute_all_costing', string='Installation Material')
    service_material = fields.Float(compute='compute_all_costing', string='Service Material')
    grand_total = fields.Float(compute='compute_all_costing', string='Grand Total')

