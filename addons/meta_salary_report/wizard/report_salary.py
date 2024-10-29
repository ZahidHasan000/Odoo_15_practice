from datetime import datetime

from odoo import models, fields


class PartnerXlsax(models.Model):
    _name = 'meta_salary_report.report_name_py'

    month = fields.Date(string="Start Date", default=datetime.today())
    salary_structure = fields.Many2one('hr.payroll.structure', string="Salary Structure", required=True)

    def button_export_xlsx(self):
        # getting data
        employee_list = self.env['hr.payslip'].search([], order='bank_order asc')
        datas = []
        for i in employee_list:
            if i.date_from <= self.month <= i.date_to:
                datas.append(i.id)
        data_finals = {
            "ids": datas,
            "month": self.month.month,
            "year": self.month.year,
            "salary_structure": self.salary_structure.id
            }
        return self.env.ref("meta_salary_report.report_names_xlsxs").report_action(
            self, data=data_finals
        )

    def button_export_pdf_bank(self):
        # getting data
        employee_list = self.env['hr.payslip'].search([], order="bank_order asc")
        datas = []
        for i in employee_list:
            if i.date_from <= self.month <= i.date_to:
                datas.append(i.id)
        data_finals = {
            "ids": datas,
            "month": self.month.month,
            "year": self.month.year
        }
        return self.env.ref("meta_salary_report.report_names_pdf_bank").report_action(
            self, data=data_finals
        )
