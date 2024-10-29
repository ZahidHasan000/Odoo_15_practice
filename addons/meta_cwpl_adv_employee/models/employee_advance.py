# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime


class CustomHrExpense(models.Model):
    _name="employee.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Advance'
    
    def _default_ea_account(self):
        print("I am DEfault")
        account_records = self.env['account.account'].search([('code','=','12340002')])
        
        return account_records.id
    
    def _default_ea_journal(self):
        print("I am DEfault")
        journal_records = self.env['account.journal'].search([('id','=',32)])
        
        return journal_records.id
        
        
    name=fields.Char(string="EA Code",required=True, copy=False, default=lambda self: 'New', tracking=True)
    
    ea_created_by = fields.Many2one(
        'res.users', string='Created By', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True,readonly=True)
    
    ea_description=fields.Text(string="Description",tracking=True)
    
    ea_avbance_for=fields.Many2one(comodel_name='hr.employee', string='Advance for',tracking=True)
    
    ea_project=fields.Many2one(comodel_name="account.analytic.account",string="Project",tracking=True)
    
    ea_account=fields.Many2one(comodel_name="account.account", string="Advance Account", required=1,
                               domain="[('is_advance_account', '=', True)]")
    
    ea_journal=fields.Many2one(comodel_name="account.journal",string="Default Employee Advance",default=lambda self: self._default_ea_journal())
    
    ea_payment_acc=fields.Many2one(comodel_name="account.account",domain="[('user_type_id.name', '=', 'Bank and Cash')]" ,string="Payment Account")
    
    ea_journal_entry_ref=fields.Many2one(comodel_name="account.move",string="Journal Entry Ref")
    
    ea_amount=fields.Float(string="Advance Amount",tracking=True)
    
    state = fields.Selection([
        ('draft', 'User'),
        ('check', 'Checker'),
        ('approve', 'Approved By'),
        ('posted', 'Posted'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
        
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('employee.advance') or _('New')
        res = super(CustomHrExpense, self).create(vals)
        return res
    
    def get_journal_hit(self):
        ac_move=self.env['account.move']
        
        currency_name=self.env['res.currency'].search([('name','=','BDT')])
        current_date=str(datetime.now().date())
        only_date=datetime.strptime(current_date, "%Y-%m-%d")
        
        acc_values={
            "ref":f"Advance To Employee Reference {self.name}",
            "journal_id":self.ea_journal.id,
            "date":only_date,
            "move_type":"entry",
            "state":"draft",
            "currency_id":currency_name.id,
            "employee_advance_source":self.id, 
        }
        print("Account Move Values------->",acc_values)
        ac_move_created=ac_move.create(acc_values)
        self.ea_journal_entry_ref=ac_move_created.id
        print("Account Move Created--------->",ac_move_created)
        
        # for rec in range(0,2):
        #     mv_lines.append(rec)
            
        # mv_lines=[]
        if ac_move_created:
            ac_move_line=self.env['account.move.line']
            default_mv_line_vals = ac_move_line.default_get(ac_move_line._fields.keys())
            
            mv_lines=[(0,0,dict(
                            default_mv_line_vals,
                            move_id=ac_move_created.id,
                            currency_id=currency_name.id,
                            account_id=self.ea_account.id,
                            partner_id=self.ea_avbance_for.address_home_id.id,
                            name=self.ea_description,
                            debit=self.ea_amount,
                            credit=0.0,
                            )),
                            (0,0,dict(
                            default_mv_line_vals,
                            move_id=ac_move_created.id,
                            currency_id=currency_name.id,
                            account_id=self.ea_payment_acc.id,
                            partner_id=self.ea_avbance_for.address_home_id.id,
                            name=self.ea_description,
                            credit=self.ea_amount,
                            debit=0.0,
                            ))]
        
        print("Account Move Line Created--------->",mv_lines)
        ac_move_created.update(dict(line_ids=mv_lines))
        self.write({'state': 'posted'})
        
    def user_send_to_checker(self):
        for rec in self:
            rec.write({'state': 'check'})

    def user_reject(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def checker_send_to_approver(self):
        for rec in self:
            rec.write({'state': 'approve'})

    def checker_reject(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def approver_reject(self):
        for rec in self:
            rec.write({'state': 'cancel'})
        
    