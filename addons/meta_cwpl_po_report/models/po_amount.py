# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from num2words import num2words
import logging

class POAmountWord(models.Model):
    _inherit="purchase.order"
    
    a2w=fields.Text(string="Amount In Word",compute='amount_in_words')
    
    @api.depends('amount_total')
    def amount_in_words(self):
        for rec in self:
            eu='euro'
            ce='cents'
            # bdt="taka"
            # paisa='paisa'
            
            amount2w= num2words(rec.amount_total, to='currency', lang='en_US').capitalize()            
            # logging.info(f"Amount In Word for the PO: {rec.name} is {amount2w}")
            
            if (eu in amount2w) and (ce in amount2w):
                am2w=amount2w.replace(eu, (rec.currency_id.currency_unit_label).lower())                
                am2w=am2w.replace(ce, (rec.currency_id.currency_subunit_label).lower())
                rec.a2w=am2w
            else:
                rec.a2w=amount2w