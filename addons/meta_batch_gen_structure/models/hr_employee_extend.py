# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _

class hrEmployeeExtend(models.Model):
    _inherit = 'hr.employee'
    
    extended_structure_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    
    # extended_structure_id = fields.Many2one(related="slip_ids.struct_id.id",string="Salary Structure")
    
    # @api.depends("extended_structure_id")
    # def _get_date_from_joining(self):
    #     print("-----------i am in---------------")
    #     for x_employees in self:
    #         payslip_run_custom=self.env["hr.payslip.run"].search([()])
    #         for hr_p_run in payslip_run_custom:
                
    #             if x_employees.extended_structure_id:
                    
    #                 # dt=(datetime.now()).date()
    #                 dt=hr_p_run.date_start
    #                 dt_str=str(dt)
    #                 dt_lst=dt_str.split('-',2)
    #                 dt_day=int(dt_lst[2])
    #                 print("DT DAY------------------>",dt_day)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                    
    #                 if dt_day>1:                    
    #                     payslip_employee_data=self.env["hr.payslip"].search([()])
    #                     for empl in payslip_employee_data:
    #                         empl.date_from=empl.employee_id.x_studio_joining_date