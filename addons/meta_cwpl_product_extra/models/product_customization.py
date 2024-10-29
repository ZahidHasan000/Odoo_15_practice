# -*- coding: utf-8 -*-

from odoo import models, fields, api

    
    
class GensetBrand(models.Model):
    _name="genset.brand"
    _description="Genset Brand"
    
    name=fields.Char(string="Brand Name")
    control_module=fields.Char(string="Control Module")
    port_of_shipment=fields.Char(string="Port of Shipment")
    
class AlternatorBrand(models.Model):
    _name="alternator.brand"
    _description="Alterantor Brand"
    
    name=fields.Char(string="Name")
    
class EngineBrand(models.Model):
    _name="engine.brand"
    _description="Engine Brand"
    
    name=fields.Char(string="Name")

    
class ProductExtra(models.Model):
    _inherit="product.template"
    
    part_number = fields.Char(string="Part Number")
    need_spec = fields.Boolean(string="Specifications",default=False)
    gen_brand = fields.Many2one(comodel_name="genset.brand",string="Genset Brand")
    prime_rating = fields.Char(string="Prime Rating(KVA)")    
    standby_rating = fields.Char(string="Standby Rating(KVA)")    
    genset_model = fields.Char(string="Gen Set Model")    
    alt_brand = fields.Many2one(comodel_name="alternator.brand",string="Alternator Brand")    
    alt_model = fields.Char(string="Alternator Model")    
    eng_brand = fields.Many2one(comodel_name="engine.brand",string="Engine Brand")
    eng_model=fields.Char(string="Engine Model")
    tank_capacity=fields.Char(string="Tank Capacity")
    fule_consumption=fields.Char(string="Fuel Consumption")
    dimention_open=fields.Char(string="Dimention(Open) cm")
    dimention_canopied=fields.Char(string="Dimention(Canopied) cm")
    weight_open=fields.Char(string="Weight(Open) kg")
    weight_canopied=fields.Char(string="Weight(Canopied) kg")
    
    _sql_constraints = [
        ('default_code_uniq', 'unique (default_code)', "The Product Code must be unique, this one is already assigned to another Product.")
    ]
    
    