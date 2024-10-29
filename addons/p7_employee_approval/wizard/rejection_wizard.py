from odoo import api, fields, models, _


class P7EmployeeRejectionWizard(models.TransientModel):
    _name = 'employee.rejection.wizard'
    _description = 'Employee Rejection'

    rejection_reason = fields.Char(string="Rejection Reason")
    employee_id = fields.Many2one('hr.employee')

    def button_confirm_reject(self):
        """Rejection maill will send."""
        email_values = {'user': self.employee_id.create_uid.login, 'name': self.employee_id.create_uid.name,'reason':self.rejection_reason}
        self.env.ref('p7_employee_approval.reject_mail_template').with_context(
            order=email_values).send_mail(self.employee_id.id, force_send=True) 
        self.employee_id.write({'state':'reject',})