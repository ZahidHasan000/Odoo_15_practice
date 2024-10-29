from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HR_employee_base(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # Added the log tracker for these fields
    work_phone = fields.Char('Work Phone', compute="_compute_phones", store=True, readonly=False,tracking=True)
    mobile_phone = fields.Char('Work Mobile', compute="_compute_work_contact_details", store=True, inverse='_inverse_work_contact_details',tracking=True)
    department_id = fields.Many2one('hr.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    parent_id = fields.Many2one('hr.employee', 'Manager', compute="_compute_parent_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    coach_id = fields.Many2one(
        'hr.employee', 'Coach', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" has no specific rights or responsibilities by default.',tracking=True)
    work_email = fields.Char('Work Email', compute="_compute_work_contact_details", store=True, inverse='_inverse_work_contact_details',tracking=True)