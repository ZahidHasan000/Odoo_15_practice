from odoo import models, fields, api, _


class p7_employee_approval(models.Model):
    _inherit = 'hr.employee'

    # Added state field
    state = fields.Selection([
        ('draft', 'HR Manager'),
        ('approval1', 'MD Approval'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Status', copy=False,
       tracking=True, help='Status of the Employee', default='draft') 
    to_show_statusbar = fields.Boolean(related="company_id.send_mail_for_employee_approvals")
 
    @api.model
    def create(self,vals):
        """Created Records will be archived if boolean is enabled. It will not be visible anywhere"""
        res = super(p7_employee_approval,self).create(vals)
        if self.env.company.send_mail_for_employee_approvals:
            res.active = False 
        return res

    def action_send_for_approval(self):
        """Mail will send to Manager after clicking the button"""
        approval_user_groups = self.env['res.groups'].sudo().search([('name', '=', 'Allow Employee Approval')])
        for item in approval_user_groups.users:
            email_values = {'user': item.login, 'name': item.name}
            self.env.ref('p7_employee_approval.to_approve_mail_template').with_context(
                order=email_values).send_mail(self.id, force_send=True)
        self.write({'state': 'approval1'})
        
    def action_approved(self):
        """Approved mail will send to record created user. And employee will be visisble everywhere"""
        email_values = {'user': self.create_uid.login, 'name': self.create_uid.name}
        self.env.ref('p7_employee_approval.new_approved_mail_template').with_context(
            order=email_values).send_mail(self.id, force_send=True)
        self.write({'active': True,'state':'approve'})  

    def action_rejection(self):
        """Rejection mail will send to record created user. Capturing the reason also"""
        rejection_form = self.env.ref('p7_employee_approval.employee_rejection_wizard_form_view')
        return {
            'name': _('Employee Rejection Reason'),
            'res_model': 'employee.rejection.wizard',
            'view_mode': 'form',
            'views': [(rejection_form.id, 'form')],
            'view_id': rejection_form.id,
            'context': {
                'active_model': 'hr.employee',
                'active_ids': self.ids,
                'default_employee_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        
    def action_reset_to_draft(self):
        """After Rejection this button will be visible"""
        self.state = 'draft'
    

    
    



