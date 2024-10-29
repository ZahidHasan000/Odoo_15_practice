# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date



class meta_extra_contact_field(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    # _description = 'meta_extra_contact_field.meta_extra_contact_field'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        active_employee_ids = self.env.context.get('active_employee_ids', False)
        if active_employee_ids:
            return self.env['hr.employee'].browse(active_employee_ids)
        # YTI check dates too
        return self.env['hr.employee'].search(self._get_available_contracts_domain())

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    default=lambda self: self._get_employees(), required=True,
                                    compute='_compute_employee_ids', store=True, readonly=False)
    structure_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    department_id = fields.Many2one('hr.department')

    @api.depends('department_id','structure_id')
    def _compute_employee_ids(self):
        for wizard in self:
            domain = wizard._get_available_contracts_domain()
            if wizard.department_id:
                domain = expression.AND([
                    domain,
                    [('department_id', 'child_of', self.department_id.id)],
                ])
            else:
                domain = expression.AND([
                    domain,
                    [('extended_structure_id','=', self.structure_id.id)]
                ])
                
            wizard.employee_ids = self.env['hr.employee'].search(domain)
