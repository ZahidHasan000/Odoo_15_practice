# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)



class EmployeeDetails(models.Model):
    _inherit="hr.employee"

    loan_details_line_ids=fields.One2many(comodel_name='employee.loan.details',inverse_name='employee_id',string="Employee Loans",copy=False)

class EmployeeLoanDetails(models.Model):
    _name = 'employee.loan.details'
    _description = 'Employee Loan Details'

    employee_id=fields.Many2one(comodel_name='hr.employee',string="Employee",index=True,readonly=True, auto_join=True, ondelete="cascade")
    l_date=fields.Date(string="Date", default=fields.Date.context_today)
    l_principal=fields.Float(string="Loan Principal")
    # l_principal_deduction=fields.Float(string="Loan Principal Deduction",compute='_compute_loan_balance')
    l_principal_deduction=fields.Float(string="Loan Principal Deduction",compute='_compute_l_principal_deduction',store=True)
    l_balance=fields.Float(string="Loan Balance",compute='_compute_loan_balance')
    l_remark=fields.Char(string='Remarks')
    

    @api.depends('l_date','employee_id.slip_ids.state')
    def _compute_l_principal_deduction(self):
        for record in self:
            l_principal_deduction = 0.0            
            _logger.info(f"record.l_date: {type(record.l_date) }{record.l_date} ----- record.employeee_id.slip_ids { record.employee_id.slip_ids.mapped('date_from') }")
            _logger.info(f"record.l_date: {record.l_date} ----- record.employee_id.slip_ids { record.employee_id.slip_ids.mapped('date_to') }")
            _logger.info(f"record.employee_id.slip_ids.line_ids.codes { record.employee_id.slip_ids.mapped('input_line_ids.input_type_id.code') }")
            for slip_id in record.employee_id.slip_ids.filtered(lambda s: s.state=='done' and s.date_from <= record.l_date <= s.date_to):
                _logger.info(f"slip_line.input_line_ids.input_type_id.code {slip_id.mapped('input_line_ids.input_type_id.code')}")
                for slip_line in slip_id.input_line_ids.filtered(lambda sl: sl.input_type_id.code =='LPD' ):

                    _logger.info(f"slip_line.amount {slip_line.mapped('amount')}")
                    l_principal_deduction+=slip_line.amount
                    remark=slip_id.payslip_run_id.name
                    record.l_remark=remark
            _logger.info(f"l_principal_deduction : {l_principal_deduction}")
            record.l_principal_deduction = l_principal_deduction
            

    
    @api.depends("l_principal", "l_principal_deduction")
    def _compute_loan_balance(self):
        for record in  self:
            _logger.info(f"record.l_principal : {record.l_principal} - record.l_principal_deduction: {record.l_principal_deduction} == {record.l_principal - record.l_principal_deduction}")
            record.l_balance = record.l_principal - record.l_principal_deduction
