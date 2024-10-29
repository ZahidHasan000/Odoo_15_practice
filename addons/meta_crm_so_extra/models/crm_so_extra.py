# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import logging,time

class CRMSoExtra(models.Model):
    _inherit = 'sale.order' 

    # team_id = fields.Many2one(
    #     'crm.team', 'Sales Team',
    #     ondelete="set null", tracking=True,
    #     change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    so_business_prod_type = fields.Selection([
        ('genset', 'Genset'),
        ('bbt', 'BBT'),
        ('sub_station', 'Substation'),
        ('project', 'Project'),
        ('',''),
    ],string='Business Product Type',default='')
    
    crm_generated=fields.Boolean(string="Is Crm Generated",default=False)
    
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,)
    
    so_salesperson=fields.Many2one(comodel_name="hr.employee",string="Salesperson")
    so_warranty_applicable_from = fields.Selection([
        ('wfd', 'Warranty From Delivery'),
        ('wfc', 'Warranty From Commisioning'),        
    ],string='Warranty Applicable From')
    so_warranty_p_day=fields.Integer(string="Warranty Period(Days)",default=0)
    so_warranty_p_hour=fields.Integer(string="Warranty Period(Hours)",default=0)
    so_do_com_date=fields.Date(string="DO/Commission Date")
    so_warranty_note=fields.Char(string="Warranty Note")
    
    so_delivery_option=fields.Selection([
        ('do', 'Delivery Only(I&C is not in CWPL Scope)'),
        ('inc', 'Including I&C'),        
    ],string='Delivery Option')
    i_n_c_status=fields.Selection([
        ('',''),
        ('done', 'Done'),
        ('not_done', 'Not Done'),        
    ],string='I&C Status',default='')
    
    so_offer_type=fields.Selection([
        ('local', 'Local Sale'),
        ('cnf', 'C&F Sale'),        
    ],string='Sales Type')
    
    so_principle=fields.Many2one(comodel_name="res.partner",string="Principle")
    so_po_order=fields.Many2one(comodel_name="purchase.order",string="Purchased Order")
    so_project_name=fields.Char(string="Project Name")
    
    so_product_model=fields.Char(string="Product Model")
    so_customer_po_date=fields.Date(string="Customer PO Date")
    so_customer_po_number=fields.Char(string="Customer PO Number")
    
    so_paymet_term=fields.Char(string="Payment Terms")
    # so_vat_ait=fields.Selection(related="opportunity_id.local_vat_n_ait",string='VAT and AIT',readonly=False)
    
    so_vat_ait=fields.Selection(
        [('included', 'Included'),
        ('excluded', 'Excluded'),
        ('not_mentioned', 'Not Mentioned')
        ],string='VAT and AIT',readonly=False)
    
    so_crm_notes=fields.Char(string="CRM Notes")
    so_commissioning_comment=fields.Char(string="Commissioning Comment")
    so_finance_notes=fields.Char(string="Finance Notes")
    so_project_budget=fields.Float(string="Project Budget")
    so_pr_raised=fields.Float(string="PR Raised")
    so_po_issued=fields.Float(string="PO Issued")
    
    to_b_executed_by=fields.Many2one(comodel_name="res.users",string="To Be Executed By")
    site_visit_report=fields.Selection([
        ('not_submitted', 'Not Submitted'),        
        ('in_progress', 'In Progress'),        
        ('submitted', 'Submitted'),
    ],string='Site Visit Report',default='not_submitted')
    enginner_review=fields.Selection([
        ('pending', 'Pending'),        
        ('in_progress', 'In Progress'),        
        ('done', 'Done'),
    ],string='Enginnering Review',default='pending')
    
    invoice_paid=fields.Float(string="Total Invoice",compute="get_invoice_amounts")
    invoice_due=fields.Float(string="Remaining Invoice",compute="get_invoice_amounts")
    
    total_fix_discount=fields.Float(string="Total Fix Discount",compute="get_fix_discount")
    
    # analytic_account_id = fields.Many2one(
    #     'account.analytic.account', 'Analytic Account',
    #     compute='_compute_analytic_account_id', store=True,
    #     readonly=False, copy=False, check_company=True,  # Unrequired company
    #     states={'check': [('required', True)],'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     help="The analytic account related to a sales order.")
    
    # def _get_vat_ait(self):
    #     for so in self:
    #         if so.opprtunity_id.local_vat_n_ait:
    #             so.so_vat_ait=so.opprtunity_id.local_vat_n_ait
    
    # @api.model
    # def _get_default_team(self):
    #     return self.env['crm.team']._get_default_team_id()
    
    def get_fix_discount(self):
        for rec in self:
            rec.total_fix_discount = sum(rec.order_line.mapped('fix_discount'))
    
    def get_invoice_amounts(self):
        for rec in self:
            # sum(invoice.amount_total for invoice in self.invoice_ids)
            # inv_data=self.invoice_ids
            rec.invoice_paid=sum(rec.invoice_ids.mapped('amount_total'))
            rec.invoice_due=rec.amount_total-rec.invoice_paid
            # rec.invoice_due=sum(rec.invoice_ids.mapped('amount_residual'))
            logging.info(f'invoice total------------------> {rec.invoice_paid}')
            logging.info(f'invoice total------------------> {rec.invoice_due}')
            
            
    
    @api.onchange('so_business_prod_type')
    def _compute_dynamic_domain(self):
        # c=[]
        # d=[]
        # a=self.env['sale.order'].search([('team_id.member_ids', 'in', [self.env.user.id])])
        # # a=self.env['sale.order'].search([('user_id.id', 'in', [self.team_id.member_ids.id])])
        # for b in a :
        #     c.append(b.name)
        #     d.append(b.user_id)
        
        # print("Sale Orders Count:-------------->",len(c))                 
        # print("Sale Orders name:-------------->",c)                 
        # print("Sale Orders salesperson:-------------->",d)                 
        # print("Sale Orders Teamid:-------------->",self.team_id.member_ids)                 
            
        for rec in self:
            print("SO Business Prod Type-------------->",rec.so_business_prod_type)                 
            if rec.so_business_prod_type=='genset':            
                # res={'domain': {'partner_id': ['&',('genset', '=', True),'|',('customer_id_gnst.parent_id.name', '=', rec.user_id.employee_id.name),('customer_id_gnst.name', '=', rec.user_id.employee_id.name)]}}
                
                res={'domain': {'partner_id': ['&',('genset', '=', True),('customer_id_gnst.user_id.id', 'in', rec.team_id.member_ids.ids)]}}
                
                print("res Domain -------------->",res)
                
            elif rec.so_business_prod_type=='bbt':            
                res={'domain': {'partner_id': ['&',('bbt', '=', True),('customer_id_bbt.user_id.id', 'in', rec.team_id.member_ids.ids)]}}
                
            elif rec.so_business_prod_type=='sub_station':            
                res={'domain': {'partner_id': ['&',('sub_station', '=', True),('customer_id_sub_station.user_id.id', 'in', rec.team_id.member_ids.ids)]}}
                
            elif rec.so_business_prod_type=='project':   
                res={'domain': {'partner_id': ['&',('project', '=', True),('customer_id_project.user_id.id', 'in', rec.team_id.member_ids.ids)]}}
            else:
                res={'domain': {'partner_id': []}}
                
        return res

    @api.onchange('partner_id')
    def _compute_dynamic_sp_domain(self):
        for rec in self:
            print("SO Business Prod Type-------------->",rec.so_business_prod_type)                 
            if rec.so_business_prod_type=='genset':            
                res={'domain': {'so_salesperson': [('id', '=', rec.partner_id.customer_id_gnst.id)]}}
                print("res Domain -------------->",res)
            elif rec.so_business_prod_type=='bbt':            
                res={'domain': {'so_salesperson': [('id', '=', rec.partner_id.customer_id_bbt.id)]}}
            elif rec.so_business_prod_type=='sub_station':            
                res={'domain': {'so_salesperson': [('id', '=', rec.partner_id.customer_id_sub_station.id)]}}
            elif rec.so_business_prod_type=='project':
                res={'domain': {'so_salesperson': [('id', '=', rec.partner_id.customer_id_project.id)]}}
            else:
                res={'domain': {'so_salesperson': []}}
                
        return res
    
    def checker_send_quotation_to_approval(self):
        for rec in self:
            if rec.message_attachment_count>0:
                rec.write({'state': 'to approve'})
            else:
                raise UserError(_('Please Add An Attachment To Move Forward'))
    

class CustomSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    fix_discount = fields.Float(string='Fixed Disc')
    
    # @api.depends('fix_discount')
    # def get_sub_total(self):
    #     for rec in self:
    #         reg_subtotal=rec.price_subtotal
    #         rec.price_subtotal= reg_subtotal-rec.fix_discount
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','fix_discount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            if line.fix_discount>0:
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded']-line.fix_discount,
                })
            else:
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            
#     route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)], ondelete='restrict', check_company=True)
    
#     product_type = fields.Selection(related='product_id.detailed_type')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    def _create_invoice(self, order, so_line, amount):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))
        for sale in sale_orders:
            if self.advance_payment_method == 'percentage' and self.amount>0:
                inv_amount=sale.amount_total*(self.amount/100)
            if (self.advance_payment_method == 'percentage' and inv_amount >sale.invoice_due) or (self.advance_payment_method == 'fixed' and  self.fixed_amount > sale.invoice_due):
                raise UserError(_('The value of the down payment amount must not exceed the total sale value.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_invoice_values(order, name, amount, so_line)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id

        invoice = self.env['account.move'].with_company(order.company_id)\
            .sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice