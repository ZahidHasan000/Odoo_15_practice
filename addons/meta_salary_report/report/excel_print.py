from odoo import models, api
import calendar
import json
import logging
from datetime import datetime


class PartnerXlsx(models.AbstractModel):
    _name = 'report.meta_salary_report.report_name_py_xls'
    _inherit = 'report.report_xlsx.abstract'

    def _get_report_values(self, docids, data):
        return data

    def generate_xlsx_report(self, workbook, data, partners):
        # prepare excel sheet
        format1 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 11, 'align': 'vcenter'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        sheet = workbook.add_worksheet('Salary Sheet')
        # header
        month = data['month']
        salary_structure = data['salary_structure']
        # logging.warning("Salary Structure---------->%s",salary_structure)
        
        
        payslip_id = self.env["hr.payslip"].search([('id', 'in', data['ids']),('struct_id','=',salary_structure)])
        company_name = self.env['res.company'].search([], limit=1).name

        # logging.warning("Payslip ID---------->%s",payslip_id)
        # logging.warning("Payslip ID---------->%s",len(payslip_id))
        sheet.write(1, 1, payslip_id[0].company_id.name, format2)
        sheet.write(2, 1, 'Salary Sheet:', format2)
        sheet.write(2, 2, calendar.month_name[month] + ' - ' + str(data["year"]), format2)
        sheet.write(3, 1, 'Date of Disbursement', format2)
        sheet.write(4, 1, 'Report Generation Date', format2)
        sheet.write(4, 2, datetime.now().date(), date_format)
        # column name

        sheet.write(5, 1, 'ID', format1)
        sheet.write(5, 2, 'Full Name', format1)
        sheet.write(5, 3, 'Designation', format1)
        # sheet.write(5, 4, 'Grade', format1)
        sheet.write(5, 4, 'Cost Center', format1)
        sheet.write(5, 5, 'Department', format1)
        sheet.write(5, 6, 'Workstation', format1)
        sheet.write(5, 7, 'Date of Joining', format1)
        sheet.write(5, 8, 'DBBL Account Number', format1)
        sl = 8
        all_rule = {}
        rule_name = []
        rule_code = []
        rule_seq = []
        pdf_rule_seq_list = []  # List to store pdf_rule_seq

        rule = self.env['hr.payroll.structure'].search([('id', '=', salary_structure)]).rule_ids
        for i in rule:
            # if i.code not in rule_code and i.code != "LPD":
            if i.code not in rule_code and i.pdf_rule_seq>0:
                rule_name.append(i.rule_name)
                rule_code.append(i.code)
                rule_seq.append(i.sequence)
                pdf_rule_seq_list.append(i.pdf_rule_seq)
        #_________Sort Using Sequence________________#
        # for i in range(0, len(rule_seq)):
        #     all_rule[rule_seq[i]] = rule_name[i], rule_code[i]

        for i in range(0, len(pdf_rule_seq_list)):
            all_rule[pdf_rule_seq_list[i]] = rule_name[i], rule_code[i]

        all_rule_sort = sorted(all_rule.items())

        for i in all_rule_sort:
            sl = sl + 1
            sheet.write(5, sl, i[1][0], format1)

        new_sl=sl+1
        sheet.write(5, new_sl, 'Principle', format1)
        sheet.write(5, new_sl+1, 'Loan Principal Deduction', format1)
        sheet.write(5, new_sl+2, 'Balance', format1)

        # table body
        row = 6
        total = {}
        date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
        for each_data in payslip_id:
            contract_info = self.env['hr.contract'].sudo().search([('employee_id', '=', each_data.employee_id.id)])

            sheet.write(row, 1, each_data.employee_id.barcode, format2)
            sheet.write(row, 2, each_data.employee_id.name, format2)
            sheet.write(row, 3, each_data.employee_id.job_id.name, format2)
            # sheet.write(row, 4, contract_info.grade_field, format2)
            sheet.write(row, 4, contract_info.analytic_account_id.name, format2)
            sheet.write(row, 5, each_data.employee_id.department_id.name, format2)
            sheet.write(row, 6, each_data.employee_id.work_location_id.name, format2)
            sheet.write(row, 7, each_data.employee_id.x_studio_joining_date, date_style)
            sheet.write(row, 8, each_data.employee_id.bank_account_id.acc_number, format2)
            
            # Get loan details for the employee
            loan_details = each_data.employee_id.loan_details_line_ids
            if loan_details:
                principle = sum(loan_details.filtered(lambda x: each_data.date_from <= x.l_date <= each_data.date_to).mapped('l_principal'))
                principle_deduction = sum(loan_details.filtered(lambda x: each_data.date_from <= x.l_date <= each_data.date_to).mapped('l_principal_deduction'))
                balance = sum(loan_details.filtered(lambda x: each_data.date_from <= x.l_date <= each_data.date_to).mapped('l_balance'))
                sheet.write(row, new_sl, principle, format2)
                sheet.write(row, new_sl+1, principle_deduction, format2)
                sheet.write(row, new_sl+2, balance, format2)

                total[new_sl] = total.get(new_sl, 0) + principle
                total[new_sl + 1] = total.get(new_sl + 1, 0) + principle_deduction
                total[new_sl + 2] = total.get(new_sl + 2, 0) + balance
            else:
                sheet.write(row, new_sl, 0, format2)
                sheet.write(row, new_sl+1, 0, format2)
                sheet.write(row, new_sl+2, 0, format2)

            col = 8
            for i in all_rule_sort:
                col = col + 1
                try:
                    total[col]
                except KeyError:
                    total[col] = 0
                for j in each_data.line_ids:
                    if i[1][1] == j.code:
                        total[col] = total[col] + j.amount
                        sheet.write(row, col, j.amount, format2)
                        break
            row = row + 1

        col = 8
        sheet.write(row, 2, "Total", format2)
        for i in total.keys():            
            col = col + 1
            sheet.write(row, col, total[i], format2)

        logging.info(f"Total Data from payslip salaray summary excel---------------->{total}")

class ReportClassName(models.AbstractModel):
    _name = 'report.meta_salary_report.report_name_pdf_print'

    def _get_report_values(self, docids, data):
        docids = data['ids']
        return {
            'data': data,
            'docs': data
        }

