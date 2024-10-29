# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, Command, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils, convert_file, html2plaintext
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class HrPayslipCustom(models.Model):
    _inherit='hr.payslip'
    
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), '|', ('active', '=', True), ('active', '=', False)]")
    
    # struct_id = fields.Many2one(
    #     related='employee_id.extended_structure_id', string='Structure',
    #     store=True, readonly=True,
    #     states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]},
    #     help='Defines the rules that have to be applied to this payslip, according '
    #          'to the contract chosen. If the contract is empty, this field isn\'t '
    #          'mandatory anymore and all the valid rules of the structures '
    #          'of the employee\'s contracts will be applied.')
    
    # date_from = fields.Date(
    #     string='From', readonly=True, required=True,
    #     default=lambda self: fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    
    
    # date_from = fields.Date(
    #     string='From', readonly=True, required=True,
    #     default=lambda self: fields.Date.to_string(self.employee_id.x_studio_joining_date) if (int((date.today()).strftime("%m"))==int((fields.Date.to_string(self.employee_id.x_studio_joining_date).strftime("%m")))) and (int((fields.Date.to_string(self.employee_id.x_studio_joining_date)).strftime("%d"))>1) else fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    
    # @api.depends('employee_id')
    # def _compute_struct_id(self):
    #     for slip in self:
    #         slip.struct_id = slip.employee_id.extended_structure_id
    
    date_from_joining=fields.Date(string="Employee Joing Date", compute='_get_date_from_joining')
    
    print("Today month------------->",int((date.today()).strftime("%m")))
    # print("Joining Date day------------->",date_from_joining.strftime('%Y-%m-%d'))
    # print("Joining Date day------------->",date_from_joining)
    
    
    # date_from = fields.Date(
    #     string='From', readonly=True, required=True,
    #     default=lambda self: date(self.employee_id.x_studio_joining_date) if int((date.today()).strftime("%m"))==int(fields.Date.from_string((self.date_from_joining).to_date()).month) and (int(fields.Date.from_string((self.date_from_joining).to_date()).day)>1) else fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    
    # date_from = fields.Date(
    #     string='From', readonly=True, required=True,
    #     default=lambda self: date(self.employee_id.x_studio_joining_date) if int((date.today()).strftime("%m"))==int(datetime.strptime(str(self.date_from_joining),'%Y-%m-%d').month) and (int(datetime.strptime(str(self.date_from_joining),'%Y-%m-%d').day)>1) else fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    
    
    @api.depends("employee_id")
    def _get_date_from_joining(self):
        print("-----------i am in---------------")
                                                                 
        # payslip_run_custom=self.env["hr.payslip.run"].search([])
        for x_slip in self:
            dt=x_slip.payslip_run_id.date_start
            x_dt=x_slip.employee_id.x_studio_joining_date
            # dt=hr_p_run.date_start
            print("DT------------------>",dt)
            print("X DT------------------>",x_dt)
            print("X DT year------------------>",int(datetime.strptime(str(x_dt),'%Y-%m-%d').year))
            print("X DT type------------------>",type(x_dt))
            dt_str=str(dt)
            x_dt_str=str(x_dt)
            
            dt_lst=dt_str.split('-',2)
            x_dt_lst=x_dt_str.split('-',2)
            
            dt_day=int(dt_lst[2])
            x_dt_day=int(x_dt_lst[2])
            
            dt_month=int(dt_lst[1])
            x_dt_month=int(x_dt_lst[1])
            
            dt_year=int(dt_lst[0])
            x_dt_year=int(x_dt_lst[0])
            
            print("DT Day------------------>",dt_day)
            print("DT Month------------------>",dt_month)
            print("DT Year------------------>",dt_year)
            
            print("X DT DAY------------------>",x_dt_day)
            print("X DT Month------------------>",x_dt_month)
            print("X DT Year------------------>",x_dt_year)
            
                
                # for hr_p_run in payslip_run_custom:            
            if int(datetime.strptime(str(x_dt),'%Y-%m-%d').year)==dt_year and int(datetime.strptime(str(x_dt),'%Y-%m-%d').month)==dt_month:
                if int(datetime.strptime(str(x_dt),'%Y-%m-%d').day)>1:                    
                # payslip_employee_data=x_slip.env["hr.payslip"].search([()])
                # for empl in payslip_employee_data:
                    print("<-----------------Inside IF Statement------------------>")
                    
                    
                    # for hr_p_run in payslip_run_custom:
                    x_slip.date_from=x_slip.employee_id.x_studio_joining_date
                    print("DATE FROM------------------>",x_slip.date_from)
                
                    x_slip.date_from_joining=x_slip.employee_id.x_studio_joining_date
                    print("Date From Joining------------------>",x_slip.date_from_joining)
                else:
                    x_slip.date_from_joining=x_slip.employee_id.x_studio_joining_date
                    print("Date From Joining------------------>",x_slip.date_from_joining)
            else:
                x_slip.date_from_joining=x_slip.employee_id.x_studio_joining_date
                print("Date From Joining------------------>",x_slip.date_from_joining)
                
                