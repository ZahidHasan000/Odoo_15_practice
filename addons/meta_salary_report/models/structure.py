from odoo import api, fields, models, _


class StructureInherit(models.Model):
    _inherit = "hr.payroll.structure"

    email_sl = fields.Text(string='Email Id')
    email_to = fields.Text(string="To", default="To,")
    email_to_whom = fields.Text(string='To Whom')
    email_bank_name = fields.Text(string='Bank Name')
    email_bank_branch = fields.Text(string='Bank Branch')
    email_address = fields.Text(string='Bank Address')

    email_subject1 = fields.Char(string='Subject')
    email_dear = fields.Text(string='Dear Sir', default="Dear Sir,")
    email_body = fields.Text(string='Main Body')

    email_footer1 = fields.Text(string='Footer')
    email_footer_last = fields.Text(string='Footer Last Line')
    email_regards = fields.Text(string='Regards', default="Best Regards,")
    email_requested_by = fields.Char('Requested By Designation')
    email_requested_to = fields.Char('Requested To Designation')
