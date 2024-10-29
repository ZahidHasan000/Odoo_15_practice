# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class CRMLeadExtra(models.Model):
    _inherit = 'crm.lead'
    
    
    lead_seq = fields.Char(string='Lead Sequence', copy=False, readonly=True, lead_status={'pending': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    
    user_id = fields.Many2one(
        'res.users', string='Login', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    
    business_prod_type = fields.Selection([
        ('genset', 'Genset'),
        ('bbt', 'BBT'),
        ('sub_station', 'SubStation'),
        ('project', 'Project'),                                
        ('', ''),                        
    ],string='Product Type',default='')

    
    partner_id = fields.Many2one(
        'res.partner', string='Existing Customer', check_company=True, index=True, tracking=10,        
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    
    
    lead_status = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('discuss', 'Discuss'),
        ('rejected', 'Rejected'),
    ], string="Lead Status",default='pending')
    
    new_customer = fields.Char(string='New Customer', copy=False)
    prod_description = fields.Text(string='Product Description', copy=False)
    source_lead = fields.Char(string='Source Lead', copy=False)
    
    custom_user_id=fields.Many2one(
        'res.users', string='Login',related="user_id",
        check_company=True, index=True, tracking=True)
    
    user_employee=fields.Many2one(related='user_id.employee_id',string="something")
    
    related_to_partner=fields.Many2one('res.partner', string='Related Contact', domain="[('parent_id', '=', partner_id)]")
    
    lead_sales_person = fields.Many2one('hr.employee', string='Sales Person',domain="['|',('parent_id', '=', user_employee),('id', '=', user_employee)]",tracking=True)
    
    lead_created_by = fields.Many2one('hr.employee', string='Lead Created By',domain="['|',('parent_id', '=', user_employee),('id', '=', user_employee)]",tracking=True)

    team_id = fields.Many2one(
        'crm.team', string='Sales Team', check_company=True, index=True, tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_team_id', ondelete="set null", readonly=False, store=True)
    
    mode_of_supply = fields.Selection([
        ('ready_stock', 'Ready stock'),
        ('foreign', 'Foreign'),
        ('local_import', 'Local Import'),
        ('others', 'Others'),
        ],string='Mode Of Supply')
    
    foreign_offer=fields.Selection([
        ('uk', 'UK'),
        ('turkey', 'Turkey'),
        ('others', 'Others'),
        ],string='Foreign Offer',default='others')
    
    local_vat_n_ait=fields.Selection([('included', 'Included'),
        ('excluded', 'Excluded'),
        ('not_mentioned', 'Not Mentioned')
        ],string="Local VAT & AIT")
    
    canopy=fields.Selection([('local', 'Local'),
        ('foreign', 'Foreign'),
        ('container', 'Container'),
        ('others', 'Others'),
        ],string="Canopy")
    
    ats=fields.Selection([('local', 'Local'),
        ('foreign', 'Foreign'),
        ('container', 'Container'),
        ('others', 'Others'),
        ],string="ATS")
    
    lead_product=fields.Many2many("product.product",string="Product")
    offer_to_be_submitted=fields.Date(string="Offer To Be Submitted")
    lost_to=fields.Many2one(
        'res.partner', string='Lost To',
        index=True, ondelete='restrict', tracking=True,readonly=True)
    
    # lead_customer_address = fields.Char(string='Address')
    
    @api.onchange('business_prod_type')
    def _compute_dynamic_domain(self):
        for rec in self:
            print("Business Prod Type-------------->",rec.business_prod_type)                 
            if rec.business_prod_type=='genset':            
                res={'domain': {'partner_id': ['&','&',('genset', '=', True),('company_type','=',True),('customer_id_gnst.parent_id.name', '=', rec.user_employee.name)]}}
                print("res Domain -------------->",res)
            elif rec.business_prod_type=='bbt':            
                res={'domain': {'partner_id': ['&','&',('bbt', '=', True),('company_type','=',True),('customer_id_bbt.parent_id.name', '=', rec.user_employee.name)]}}
            elif rec.business_prod_type=='sub_station':            
                res={'domain': {'partner_id': ['&','&',('sub_station', '=', True),('company_type','=',True),('customer_id_sub_station.parent_id.name', '=', rec.user_employee.name)]}}
            elif rec.business_prod_type=='project':
                res={'domain': {'partner_id': ['&','&',('project', '=', True),('company_type','=',True),('customer_id_project.parent_id.name', '=', rec.user_employee.name)]}}
            else:
                res={'domain': {'partner_id': []}}
                
        return res
    
    @api.model
    def create(self, vals_list):
        if vals_list.get('lead_seq', _('New')) == _('New'):
            vals_list['lead_seq'] = self.env['ir.sequence'].next_by_code('crm.lead') or _('New')
        res = super(CRMLeadExtra, self).create(vals_list)
        return res
    
    def toggle_active(self):
        res = super().toggle_active()
        self.write({"lead_status":"pending"})
        return res
    
    # def action_set_lost(self):
    #     res = super().action_set_lost()
    #     self.write({"lead_status":"rejected"})
    #     self.toggle_active()
    #     return res
    
    def _create_customer(self):
        """ Create a partner from lead data and link it to the lead.

        :return: newly-created partner browse record
        """
        Partner = self.env['res.partner']
        contact_name = self.new_customer
        if not contact_name:
            contact_name = Partner._parse_partner_name(self.email_from)[0] if self.email_from else False

        if self.partner_name:
            partner_company = Partner.create(self._prepare_customer_values(self.partner_name, is_company=True))
        elif self.partner_id:
            partner_company = self.partner_id
        else:
            partner_company = None

        if contact_name:
            return Partner.create(self._prepare_customer_values(contact_name, is_company=True, parent_id=partner_company.id if partner_company else False))

        if partner_company:
            return partner_company
        return Partner.create(self._prepare_customer_values(self.name, is_company=True))
    
    
    # def action_new_quotation(self):
    #     res=super(CRMLeadExtra,self).action_new_quotation()        
    #     product_list = []
    #     so_lines=[]
    #     for lp in self.lead_product:            
    #         so_line_val={                
    #             'product_id': lp.id,
    #             'name': lp.name,
    #             'product_uom':lp.uom_id.id,
    #             'product_uom_qty': 1,
    #             'price_unit': lp.lst_price,
    #         }            
    #         so_lines.append((0, 0, so_line_val))
    #         # res['context']['default_order_line'] = so_line_val       
        
    #     print("Sale Order Line Data------------>",so_lines)
        
    #     if self.lead_product:            
    #         # for line in so_lines:
    #         res['context']['default_order_line'] = so_lines       
        
    #     return res
    
    def action_new_quotation(self):        
        print("Over Ride Action------------>3")
        # action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        so_vals = {
            # 'search_default_opportunity_id': self.id,
            # 'search_default_partner_id': self.partner_id.id,
            'opportunity_id': self.id,
            'partner_id': self.partner_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'origin': self.name,
            'state': 'draft',
            'crm_generated': True,
            'so_vat_ait':self.local_vat_n_ait,
            'source_id': self.source_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'tag_ids': [(6, 0, self.tag_ids.ids)]
        }
        if self.team_id:
            so_vals['team_id'] = self.team_id.id,
        if self.user_id:
            so_vals['user_id'] = self.user_id.id
            
        if self.business_prod_type:
            so_vals['so_business_prod_type'] = self.business_prod_type
            
        if self.lead_sales_person:
            so_vals['so_salesperson'] = self.lead_sales_person.id
        
        so_create=self.env['sale.order'].create([so_vals])
        
        if so_create:
            if self.lead_product:
                so_lines=[]
                OrderLine = self.env['sale.order.line']
                default_so_line_vals = OrderLine.default_get(OrderLine._fields.keys())
                
                for product in self.lead_product:
                    # so_line_val={                
                    #     'name': lp.name,
                    #     'product_id': lp.id,
                    #     'product_uom_qty': 1,
                    #     'product_uom':lp.uom_id.id,
                    #     'price_unit': lp.lst_price,
                    # }
                    # so_lines.append((0,0,so_line_val))
                    
                    so_lines.append((0, 0, dict(
                            default_so_line_vals,
                            product_id=product.id,
                            product_uom_qty=1,
                            price_unit= product.lst_price,
                            )
                        ))    
                
                print("Sale Order Line Data------------>",so_lines)
                
                # action['context']['default_order_line'] = so_lines
                # print("Context------------>",action['context'])
                            
                so_create.update(dict(order_line=so_lines))
                
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': so_create.id,
        }   