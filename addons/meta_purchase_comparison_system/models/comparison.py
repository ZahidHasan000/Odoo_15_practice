from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route

_STATES = [
    ("draft", "User"),
    ("check", "Check"),
    ("approve", "Approved"),
    ("cross_function", "Cross Function"),
    ("mgt", "MGT"),
    ("confirm", "Confirm"),
    ("cancel", "Canceled"),
]


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    customer_name = fields.Many2one('res.partner', string="Customer Name", index=True, tracking=True)
    customer_address = fields.Char(related='customer_name.contact_address_complete', string="Customer Address")
    project_number = fields.Many2one(string="Project Number", readonly=True,
                                     related='purchase_request.project_number')

    def button_comparison(self):
        # for rec in self:
        self.ensure_one()

        for rec in self:
            if rec.purchase_ids:
                for item in rec.purchase_ids:
                    for item2 in item.order_line:
                        item2.cs_status = ''
            else:
                pass

        self.env['comparison'].sudo().search([('requisition_id', '=', self.id),
                                              ('state', '=', 'cancel')]).unlink()
        if self.order_count > 0:

            product_ids = []
            res = {}
            id = []
            product_list = []
            for record in self.env['purchase.order'].sudo().search(
                    [('requisition_id', '=', self.id), ('state', '!=', 'cancel')]):

                for line in record.order_line.filtered(lambda l: not l.display_type):
                    po_product_name = line.product_id.name + ' [ ' + line.order_id.name + ' ]'
                    line_id = line.id
                    product_line_values = {
                        'name': po_product_name,
                        'product_line_id': line_id,
                    }
                    product_list.append((0, 0, product_line_values))

            comparison = self.env['comparison'].sudo().search([('requisition_id', '=', self.id)])
            compare_ctx = dict(
                default_requisition_id=self.id,
                default_select_product_ids=product_list,
                default_purchase_request_id=self.purchase_request.id if self.purchase_request else False,
            )
            if comparison:
                raise UserError(_('''Already a Comparison is Present if you Create new Comparison, 
                                    PLease Cancel or Delete First One'''))

            if not comparison:
                form_view2 = [(self.env.ref('meta_purchase_comparison_system.view_comparison_form').id, 'form')]

                # compare = self.env['comparison']
                # compare.create({
                #     'requisition_id': self.id,
                #     'purchase_request_id': self.purchase_request.id,
                #     'date': date.today()
                #     })
                # print(compare.name)

                return {
                    'name': 'Comparison',
                    'type': 'ir.actions.act_window',
                    'res_model': 'comparison',
                    "domain": [('requisition_id', '=', self.id)],
                    "views": form_view2,
                    'context': compare_ctx,
                }
        else:
            raise UserError(_('There is no Order/Quotation are create, first create order then press'))

    def view_comparison(self):
        comparison = self.env['comparison'].sudo().search([('requisition_id', '=', self.id)])
        form_view2 = [(self.env.ref('meta_purchase_comparison_system.view_comparison_form').id, 'form')]
        compare_ctx = dict(
            default_requisition_id=self.id,
        )

        return {
            'name': 'Comparison',
            'type': 'ir.actions.act_window',
            'res_model': 'comparison',
            "domain": [('requisition_id', '=', self.id)],
            "views": form_view2,
            "res_id": comparison.id,
            'context': compare_ctx,
        }

    comparison_ids = fields.One2many('comparison', 'requisition_id', string='Comparison')
    comparison_id = fields.Many2one('comparison', string='Comparison', store=True)

    @api.depends('comparison_ids')
    def _compute_compare_number(self):
        for requisition in self:
            requisition.comparison_count = len(requisition.comparison_ids)

    comparison_count = fields.Integer(compute='_compute_compare_number',)

    def comparison_chart(self):
        supplier_ids = [];
        product_ids = [];
        values = [];
        amt = [];
        number = [];
        supplier_id = []
        counts = 1
        for record in self.env['purchase.order'].sudo().search(
                [('requisition_id', '=', self.id), ('comparison_id', '=', False), ('state', '!=', 'cancel')]):

            # Total Amount
            amount_all = []
            tax_all = []
            for total_item_amount in record.order_line.filtered(lambda l: not l.display_type):
                currency_rate = total_item_amount.get_currency_rate()
                rate = currency_rate.get('currency_rate')
                amount_all.append(total_item_amount.product_qty * (rate * total_item_amount.price_unit))
                tax_all.append(total_item_amount.price_tax)
            # Append supplier
            total_amnt_po_line = sum(amount_all)
            total_tax_amount = sum(tax_all)
            supplier_ids.append({'supplier_id': record.partner_id.id, 'sname': record.partner_id.name,
                                 'order_no': record.name, 'warranty': record.warranty, 'pay_terms': record.payment_terms,
                                 'deli_schedule': record.delivery_schedule, 'comments': record.po_comments,
                                 'custom_duty': '{0:,.2f}'.format(record.custom_duty), 'freight_charge': '{0:,.2f}'.format(record.freight_charge),
                                 'bank_insurance': '{0:,.2f}'.format(record.bank_and_insurance), 'cf_commission': '{0:,.2f}'.format(record.c_and_f_commission),
                                 'vat_tax_total': '{0:,.2f}'.format(total_tax_amount),
                                 'total_foreign': '{0:,.2f}'.format(total_amnt_po_line + total_tax_amount + record.custom_duty + record.freight_charge + record.bank_and_insurance + record.c_and_f_commission)})
            supplier_id.append(record.partner_id.id)
            number.append(counts)
            # Append Products and quantity
            counts += 1
            for line in record.order_line.filtered(lambda l: not l.display_type):
                if values:
                    if line.product_id.id not in product_ids:
                        product_ids.append(line.product_id.id)
                        values.append({'product_id': line.product_id.id, 'product_name': line.product_id.display_name,
                                       'price': '{0:,.2f}'.format(line.price_unit), 'uom': line.product_id.uom_po_id.name,
                                       'qty': line.product_qty})
                else:
                    product_ids.append(line.product_id.id)
                    values.append({'product_id': line.product_id.id, 'product_name': line.product_id.display_name,
                                   'price': '{0:,.2f}'.format(line.price_unit), 'uom': line.product_id.uom_po_id.name,
                                   'qty': line.product_qty})

        count = 0;
        supplier_amount_total = [];
        no_of_col = 2;
        even_number = [];
        odd_number = []
        # Append amount based on the products and supplier
        for separate_values in values:
            for suppliers in supplier_ids:
                for record in self.env['purchase.order'].sudo().search(
                        [('requisition_id', '=', self.id),
                         ('partner_id', '=', suppliers['supplier_id']), ('comparison_id', '=', False), ('state', '!=', 'cancel')]):
                    for po_line in self.env['purchase.order.line'].search(
                            [('order_id', '=', record.id), ('product_id', '=', separate_values['product_id']), ('display_type', 'not in', ('line_section', 'line_note'))]):
                        currency_rate = po_line.get_currency_rate()
                        rate = currency_rate.get('currency_rate')
                        price_unit = currency_rate.get('price_unit')
                        amt.append(
                            {'total_amount': '{0:,.2f}'.format(round((po_line.product_qty * (rate * po_line.price_unit)), 2)), 'price': '{0:,.2f}'.format(po_line.price_unit),
                             'currency': po_line.order_id.currency_id.name, 'c_rate': round(rate, 2),
                             'status': po_line.cs_status})
            print("+++++++++", amt)
            values[count]['amt'] = amt
            count += 1
            amt = []
        # Generate number to create rows and columns
        total_supplier = len(number)
        if total_supplier >= 2:
            increase_by_supplier = total_supplier * no_of_col
        else:
            increase_by_supplier = no_of_col
        if total_supplier > 1:
            total_no = range(1, increase_by_supplier + 1)
            supplier_amount_total_1 = list(range(1, increase_by_supplier + 1))
        else:
            total_no = range(1, increase_by_supplier)
            supplier_amount_total_1 = list(range(1, increase_by_supplier))
        for c_number in total_no:
            if c_number % 2 == 0:
                even_number.append(c_number)
            else:
                odd_number.append(c_number)
        for record in self.env['purchase.order'].sudo().search(
                [('requisition_id', '=', self.id), ('state', '!=', 'cancel')]):
            supplier_amount_total.append(record.amount_total)
        # Update the amount in even number position
        tcount = 1
        for i in even_number:
            supplier_amount_total_1[i - 1] = supplier_amount_total[tcount - 1]
            tcount += 1
        # Update the supplier id in odd number position
        scount = 1
        for odd_no in odd_number:
            for total in total_no:
                if total == odd_no:
                    supplier_amount_total_1[odd_no - 1] = supplier_id[scount - 1]
                    scount += 1
        return ({'prc_no': self.name, 'data':values, 'supplier':supplier_ids,'purchase_requisition_id':self.id,
                                                               'number':number, 'to_no':total_no, 'column_no':even_number, 'supplier_amount_total':supplier_amount_total,
                                                                'supplier_amount_total_1':supplier_amount_total_1, 'odd_number':odd_number})


class Comparison(models.Model):
    _name = 'comparison'
    _description = 'Comparison Products'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(srting="Name", required=True, readonly=True,
                       index=True, default=lambda self: _('New'))
    purchase_id = fields.Many2one('purchase.order', string="Purchase")
    requisition_id = fields.Many2one('purchase.requisition', string="Requisition ID")
    customer_name = fields.Many2one(string="Customer Name", readonly=True, index=True, tracking=True,
                                          related='requisition_id.customer_name')
    customer_address = fields.Char(related='customer_name.contact_address_complete', string="Customer Address")
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user,
                              readonly=True)
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request', readonly=True)
    project_number = fields.Many2one(string="Project Number", readonly=True,
                                     related='purchase_request_id.project_number')

    date = fields.Date(
        string='Date',
        index=True,
        readonly=True,
        copy=False,
        default=fields.Date.context_today
    )
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )

    comments = fields.Text(string="Comments")
    selected_po_product = fields.Many2many('select.po.products', string="Selected Po Products")
    select_product_ids = fields.One2many('select.po.products', 'comparison', string="Comparison Products")

    @api.depends('state')
    def _confirm_po_count(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.confirm_order_count = len(self.env['purchase.order'].sudo().search([('comparison_id', '=', rec.id)]))

            else:
                rec.confirm_order_count = 0

    confirm_order_count = fields.Integer(compute="_confirm_po_count")

    @api.model
    def create(self, vals):
        # if not vals.get('name') or vals['name'] == _('New'):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq.po.compare') or _('New')
        return super(Comparison, self).create(vals)

    def base_url(self):
        menu_id = self.env.ref('meta_purchase_comparison_system.menu_comparison_act').id
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s&menu_id=%s' % (self.id, self._name, menu_id)

        return base_url

    @api.ondelete(at_uninstall=False)
    def _unlink_if_cancelled(self):
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete a CS, you must cancel it first.'))

    def confirm_user(self):
        return self.write({'state': 'check'})

    def user_rejected(self):
        for rec in self:
            if rec.requisition_id:
                for item in rec.requisition_id.purchase_ids:
                    for item2 in item.order_line:
                        item2.cs_status = ''
            else:
                pass
        return self.write({'state': 'cancel'})

    def confirm_checker(self):
        return self.write({'state': 'approve'})

    def checker_rejected(self):
        for rec in self:
            if rec.requisition_id:
                for item in rec.requisition_id.purchase_ids:
                    for item2 in item.order_line:
                        item2.cs_status = ''
            else:
                pass
        return self.write({'state': 'cancel'})

    def confirm_approved(self):
        return self.write({'state': 'cross_function'})

    def approved_rejected(self):
        for rec in self:
            if rec.requisition_id:
                for item in rec.requisition_id.purchase_ids:
                    for item2 in item.order_line:
                        item2.cs_status = ''
            else:
                pass
        return self.write({'state': 'cancel'})

    def confirm_cross_function(self):
        if self.requisition_id.purchase_ids:
            for rec in self.requisition_id.purchase_ids:
                rec.is_locked_order = True
        return self.write({'state': 'mgt'})

    def cross_function_rejected(self):
        for rec in self:
            if rec.requisition_id:
                for item in rec.requisition_id.purchase_ids:
                    for item2 in item.order_line:
                        item2.cs_status = ''
            else:
                pass
        return self.write({'state': 'cancel'})

    def mgt_rejected(self):
        for rec in self:
            if rec.requisition_id:
                for item in rec.requisition_id.purchase_ids:
                    item.is_locked_order = False
                    for item2 in item.order_line:
                        item2.cs_status = ''
            else:
                pass
        return self.write({'state': 'cancel'})

    def marking_product(self):
        sub_total = []
        for line in self.select_product_ids.filtered(lambda l: l.marking_product):
            if line:
                product_line = self.env['purchase.order.line'].sudo().search([('id', '=', line.product_line_id)])
                if product_line:
                    product_line.cs_status = 'Selected'
                    sub_total.append(product_line.price_subtotal)
                else:
                    product_line.cs_status = ''

            else:
                pass
        self.total_cs_value = sum(sub_total)

    total_cs_value = fields.Float('Total CS Value', readonly=1)

    def confirm_cs(self):
        # if self.requisition_id.purchase_ids:
        #     for rec in self.requisition_id.purchase_ids:
        #         rec.is_locked_order = True

        for line in self.select_product_ids.filtered(lambda l: l.marking_product):
            if line:
                order_line = self.env['purchase.order.line'].sudo().search([('id', '=', line.product_line_id)])

                order = self.env['purchase.order'].sudo().search([('id', '=', order_line.order_id.id)])
                order2 = self.env['purchase.order'].sudo().search([('against_po_id', '=', str(order_line.order_id.id))])
                if not order2:
                    order = self.env['purchase.order'].create({
                        'partner_id': order.partner_id.id,
                        'partner_ref': order.partner_ref,
                        'payment_terms': order.payment_terms,
                        'country_of_origin': order.country_of_origin.id,
                        'origin': order.requisition_id.name,
                        'requisition_id': order.requisition_id.id,
                        'customer_name': order.customer_name.id,
                        'customer_reference': order.customer_reference.id,
                        'purchase_request': order.purchase_request.id,
                        'currency_id': order.currency_id.id,
                        'against_po_id': str(order.id),
                        'comparison_id': self.id,
                        'po_comments': order.po_comments,
                        'warranty': order.warranty,
                        'delivery_schedule': order.delivery_schedule,
                        'incoterm_id': order.incoterm_id.id,
                        'po_sourcing_type': order.po_sourcing_type,
                        'custom_duty': order.custom_duty,
                        'freight_charge': order.freight_charge,
                        'bank_and_insurance': order.bank_and_insurance,
                        'c_and_f_commission': order.c_and_f_commission,
                        'order_line': [(0, 0, {
                            'name': order_line.product_id.name,
                            'product_id': order_line.product_id.id,
                            'is_cs_po': True,
                            'account_analytic_id': order_line.account_analytic_id.id,
                            'product_qty': order_line.product_qty,
                            'product_uom': order_line.product_uom.id,
                            'price_unit': order_line.price_unit,
                            'discount': order_line.discount,
                            'taxes_id': [(6, 0, order_line.taxes_id.ids)],
                        })]
                    })

                    order.write({'state': 'user'})
                    order.message_post_with_view('meta_purchase_comparison_system.track_cs_purchase_order_creation',
                                                    values={'self': order, 'origin': self},
                                                    subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                                        'mail.mt_note'))

                elif order2:
                    self.env['purchase.order.line'].create({
                        'name': order_line.product_id.name,
                        'product_id': order_line.product_id.id,
                        'is_cs_po': True,
                        'account_analytic_id': order_line.account_analytic_id.id,
                        'order_id': order2.id,
                        'product_qty': order_line.product_qty,
                        'product_uom': order_line.product_uom.id,
                        'price_unit': order_line.price_unit,
                        'discount': order_line.discount,
                        'taxes_id': [(6, 0, order_line.taxes_id.ids)],
                    })

                else:
                    pass

        return self.write({'state': 'confirm'})

    def view_confirm_po_order(self):
        self.ensure_one()

        action = {
            'name': _("Order"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids
        comparison = self.env['purchase.order'].sudo().search([('comparison_id', '=', self.id)])

        if len(comparison) == 1:
            order = comparison.id
            action['res_id'] = order
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', comparison.ids)]

        return action

    def reset_selected_product_order(self):
        for rec in self:
            rec.select_product_ids = [(5, 0, 0)]
            rec.total_cs_value = 0.00
            product_list = []
            for line in rec.requisition_id.purchase_ids.order_line.filtered(lambda l: not l.display_type):
                line.cs_status = ''
                po_product_name = line.product_id.name + ' [ ' + line.order_id.name + ' ]'
                line_id = line.id
                product_line_values = {
                    'name': po_product_name,
                    'product_line_id': line_id,
                }
                product_list.append((0, 0, product_line_values))
            rec.select_product_ids = product_list

    def cancel_confirm_cs(self):
        for rec in self:
            for line in rec.requisition_id.purchase_ids.order_line.filtered(lambda l: not l.display_type):
                line.cs_status = ''
            comparison_confirm_po = self.env['purchase.order'].sudo().search([('comparison_id', '=', rec.id)])
            for cs in comparison_confirm_po.filtered(lambda p: p.state not in ['purchase', 'done']):
                cs.is_locked_order = False
                cs.button_cancel()
                cs.unlink()

        return self.write({'state': 'cancel'})


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    po_comments = fields.Text(string="Comments")
    comparison_id = fields.Many2one('comparison', string="CS", store=True)

    against_po_id = fields.Char('Against PO ID')

    @api.model
    def create(self, vals):
        purchase = super(PurchaseOrder, self).create(vals)
        if purchase.requisition_id.comparison_id:
            purchase.comparison_id = purchase.requisition_id.comparison_id.id
        return purchase

    @api.onchange('requisition_id')
    def get_cs_id(self):
        for rec in self:
            if rec.requisition_id.comparison_id:
                rec.comparison_id = rec.requisition_id.comparison_id.id
            else:
                rec.comparison_id = False

    def comparison_chart(self):
        return ({'purchase_id': self.id})


class SelectedProductsOreder(models.Model):
    _name = 'select.po.products'

    name = fields.Char(string='Name')
    product_line_id = fields.Integer(string='Line Id')
    comparison = fields.Many2one('comparison', string='Comparison')
    marking_product = fields.Boolean(string="Select", default=False)


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    cs_status = fields.Char(string='CS Status')
    is_cs_po = fields.Boolean(string='Is CS PO', default=False)

    def get_currency_rate(self):
        for po_line in self:
            currency_rate = 0.00
            price_unit = 0.00
            if po_line.order_id.company_id.currency_id != po_line.currency_id:
                company = po_line.env.company
                date = po_line.date_order or fields.Date.today()

                # currency_rate = po_line.order_id.company_id.currency_id._get_conversion_rate(po_line.order_id.company_id.currency_id,
                #                                                            po_line.order_id.currency_id, company, date)
                # currency_rates = po_line.order_id.currency_id._get_rates(company, date)
                # currency_rate = currency_rates.get(po_line.order_id.currency_id.id)
                currency_rates = po_line.order_id.currency_id.rate_ids[0].inverse_company_rate
                currency_rate = currency_rates
            else:
                currency_rate = po_line.order_id.company_id.currency_id.rate

            return {'currency_rate': currency_rate}



    # def currency_rate(self):
    #     rate = self.get_currency_rate()
    #     print('@#@#@#@#', rate.get('price_unit'))
    #     print('########', self.get_currency_rate())


# class ComparisonInherit(models.Model):
#     _inherit = 'comparison'
#
#     @api.model
#     def create(self, vals):
#         purchase = super(ComparisonInherit, self).create(vals)
#         if purchase.requisition_id:
#             purchase.picking_type_id = purchase.requisition_id.purchase_request.picking_type_id.id
#         return purchase
