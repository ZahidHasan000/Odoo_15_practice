# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerExtra(models.Model):
    _inherit = 'res.partner'


    genset = fields.Boolean(string="Genset", default=False)
    customer_id_gnst = fields.Many2one(comodel_name='hr.employee', string='Genset Employee')
    sub_station = fields.Boolean(string="Sub-Station", default=False)
    customer_id_sub_station = fields.Many2one(comodel_name='hr.employee', string='Sub Station Employee')
    bbt = fields.Boolean(string="BBT",default=False)
    customer_id_bbt = fields.Many2one(comodel_name='hr.employee', string='BBT Employee')
    project = fields.Boolean(string="Project",default=False)
    customer_id_project = fields.Many2one(comodel_name='hr.employee', string='Project Employee')
    
    sup_items=fields.Text(string="Supplier Services/Items")
