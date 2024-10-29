from odoo import models, fields, api,_


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    send_mail_for_employee_approvals = fields.Boolean(string="Do you need Approvals for Employee Master?")


# class ResConfigSettingsInherit(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     send_mail_for_employee_approvals = fields.Boolean(string="Do you need Approvals for Employee Master?")
#
#     @api.model
#     def get_values(self):
#         """If checkbox is enabled in settings then it will enable for other companies(Multi company)"""
#         res = super(ResConfigSettingsInherit, self).get_values()
#         params = self.env['ir.config_parameter'].sudo()
#         company = self.env.company
#         res.update(
#             send_mail_for_employee_approvals = params.get_param('p7_employee_approval.send_mail_for_employee_approvals'),
#         )
#         company.update({
#             'send_mail_for_employee_approvals': params.get_param('p7_employee_approval.send_mail_for_employee_approvals'),
#         })
#         return res
#
#     def set_values(self):
#         """If checkbox is enabled in settings then it will enable for other companies(Multi company)"""
#         super(ResConfigSettingsInherit, self).set_values()
#         params = self.env['ir.config_parameter'].sudo()
#         send_mail_for_employee_approvals = self.send_mail_for_employee_approvals or False
#         params.set_param('p7_employee_approval.send_mail_for_employee_approvals', send_mail_for_employee_approvals)
