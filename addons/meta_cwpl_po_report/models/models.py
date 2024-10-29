# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class meta_cwpl_po_report(models.Model):
#     _name = 'meta_cwpl_po_report.meta_cwpl_po_report'
#     _description = 'meta_cwpl_po_report.meta_cwpl_po_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
