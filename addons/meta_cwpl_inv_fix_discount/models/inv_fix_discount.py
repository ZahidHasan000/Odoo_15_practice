# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import logging

class AMFixDiscount(models.Model):
    _inherit="account.move"
    
    project_ref=fields.Many2one(comodel_name="account.analytic.account",string="Project Number",compute="get_project_number")

    def get_project_number(self):
        for rec in self:
            if rec.invoice_origin:
                so=self.env['sale.order'].search([('name','=',rec.invoice_origin)])
                rec.project_ref=so.analytic_account_id.id
            else:
                rec.project_ref=False

class AMLFixDiscount(models.Model):
    _inherit="account.move.line"
    
    fix_discount=fields.Float(string="Fix Disc",compute="get_fix_discount")
    disc=fields.Float(string="Disc%",compute="get_fix_discount")
    
    @api.depends('sale_line_ids')
    def get_fix_discount(self):
        logging.info(f"Self Data:--------->{self}")
        for rec in self:
            if rec.move_id.state not in ['posted','cancel']:
                # rec.move_id.with_context(check_move_validity=False) #to eleminate the unbalanced journal entry error.
                if rec.sale_line_ids:
                    for line in rec.sale_line_ids:

                        logging.info(f"Sale Line Details-------------------> Downpayment :{line.is_downpayment} \n {line.product_id.name}:{line.product_id.id} \n Subtotal:{line.price_subtotal}\n Invoiced Quantity:{line.qty_invoiced}\n Delivered Quantity:{line.qty_delivered}\n")

                        if line.is_downpayment==True:
                            rec.fix_discount = line.fix_discount
                            rec.disc = line.discount
                            rec.discount = 0.0
                            rec.tax_ids = [(6, 0, line.tax_id.ids)] if line.tax_id else False
                            # rec.quantity=line.qty_invoiced
                            # rec.price_unit=line.price_unit
                            # rec.price_subtotal=line.price_unit*(rec.quantity)
                            logging.info(f"If Is Downpayment:--------->{rec.price_subtotal}")
                        else:
                            if line.order_id.so_offer_type == "cnf":
                                rec.fix_discount = line.fix_discount
                                rec.disc = line.discount
                                rec.discount = 0.0
                                rec.tax_ids = [(6, 0, line.tax_id.ids)] if line.tax_id else False
                                # rec.quantity=line.qty_delivered
                                
                                if line.price_subtotal==0:
                                    if line.qty_delivered!=0:
                                        rec.price_unit=line.price_subtotal/line.qty_delivered
                                    else:
                                        pass
                                else:
                                    if line.product_uom_qty!=0:
                                        if line.tax_id:
                                            rec.price_unit=line.price_unit
                                        else:                                            
                                            rec.price_unit=line.price_subtotal/line.product_uom_qty
                                    else:
                                        pass

                                # rec.price_subtotal=line.price_subtotal
                                logging.info(f"If not Is Downpayment:--------->{rec.price_subtotal}")
                            else:
                                rec.fix_discount = line.fix_discount
                                rec.disc = line.discount
                                rec.discount = 0.0
                                rec.tax_ids = [(6, 0, line.tax_id.ids)] if line.tax_id else False
                                # rec.quantity=line.qty_delivered
                                if line.price_subtotal==0:
                                    rec.price_subtotal=line.price_subtotal
                                else:
                                    if line.qty_delivered!=0:
                                        if line.tax_id:
                                            rec.price_unit=line.price_unit
                                        else:
                                            rec.price_unit=line.price_subtotal/line.qty_delivered
                                            # rec.price_subtotal=line.price_subtotal/line.qty_delivered
                                    else:
                                        pass
                                                                    
                                # rec.price_subtotal=line.price_subtotal
                                logging.info(f"If not Is Downpayment:--------->{rec.price_subtotal}")
                else:
                    rec.fix_discount =0.0
                    rec.disc = 0.0
            else:
                if rec.sale_line_ids:
                    for line in rec.sale_line_ids:
                        logging.info(f"Sale Line Details-------------------> Downpayment :{line.is_downpayment} \n {line.product_id.name}:{line.product_id.id} \n Subtotal:{line.price_subtotal}\nInvoiced Quantity:{line.qty_invoiced}\n Delivered Quantity:{line.qty_delivered}\n")

                        if line.is_downpayment==True:
                            rec.fix_discount = line.fix_discount
                            rec.disc = line.discount
                            #rec.discount = 0.0
                            
                        else:
                            if line.order_id.so_offer_type == "cnf":
                                rec.fix_discount = line.fix_discount
                                rec.disc = line.discount
                                #rec.discount = 0.0
                                
                            else:
                                rec.fix_discount = line.fix_discount
                                rec.disc = line.discount
                                #rec.discount = 0.0
                else:
                    rec.fix_discount =0.0
                    rec.disc = 0.0          
                
    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1

        amount_currency = price_subtotal * sign
        balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
        return {
            'amount_currency': amount_currency,
            'currency_id': currency.id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
        }
    
    def _set_price_and_tax_after_fpos(self):
        self.ensure_one()
        # Manage the fiscal position after that and adapt the price_unit.
        # E.g. mapping a price-included-tax to a price-excluded-tax must
        # remove the tax amount from the price_unit.
        # However, mapping a price-included tax to another price-included tax must preserve the balance but
        # adapt the price_unit to the new tax.
        # E.g. mapping a 10% price-included tax to a 20% price-included tax for a price_unit of 110 should preserve
        # 100 as balance but set 120 as price_unit.
        if self.tax_ids and self.move_id.fiscal_position_id and self.move_id.fiscal_position_id.tax_ids:
            price_subtotal = self._get_price_total_and_subtotal()['price_subtotal']
            self.tax_ids = self.move_id.fiscal_position_id.map_tax(self.tax_ids._origin)
            accounting_vals = self._get_fields_onchange_subtotal(
                price_subtotal=price_subtotal,
                currency=self.move_id.company_currency_id)
            amount_currency = accounting_vals['amount_currency']
            business_vals = self._get_fields_onchange_balance(amount_currency=amount_currency)
            if 'price_unit' in business_vals:
                self.price_unit = business_vals['price_unit']
    
    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
        self.ensure_one()
        return self._get_fields_onchange_subtotal_model(
            price_subtotal=self.price_subtotal if price_subtotal is None else price_subtotal,
            move_type=self.move_id.move_type if move_type is None else move_type,
            currency=self.currency_id if currency is None else currency,
            company=self.move_id.company_id if company is None else company,
            date=self.move_id.date if date is None else date,
        )
        
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        ptns=self._get_price_total_and_subtotal_model(
            price_unit=self.price_unit if price_unit is None else price_unit,
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            currency=self.currency_id if currency is None else currency,
            product=self.product_id if product is None else product,
            partner=self.partner_id if partner is None else partner,
            taxes=self.tax_ids if taxes is None else taxes,
            move_type=self.move_id.move_type if move_type is None else move_type,
            # fix_discount=self.fix_discount if fix_discount is None else fix_discount,
        )
        # logging.info(f"Price Total & Subtotal:--------------> {ptns}")
        return ptns
        
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :param fix_discount:The Fix Discount of the move.line.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        # logging.info(f"Fix Discount form gptsnm:--------------> {self.fix_discount} for {quantity} and {discount} and Price Unit {price_unit}")
        
        line_discount_price_unit = (price_unit * (1 - (discount / 100.0)))
        # logging.info(f"line_discount_price_unit gptsnm:--------------> {line_discount_price_unit}")
        subtotal = (quantity * line_discount_price_unit)
        # logging.info(f"Subtotal gptsnm:--------------> {subtotal}")
        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']-self.fix_discount
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = subtotal-self.fix_discount
            res['price_subtotal'] = subtotal-self.fix_discount
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
    
    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount , amount_currency, move_type, currency, taxes, price_subtotal,force_computation=False):
        ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
        in some accounting fields such as 'balance'.

        This method is a bit complex as we need to handle some special cases.
        For example, setting a positive balance with a 100% discount.

        :param quantity:        The current quantity.
        :param discount:        The current discount.
        :param amount_currency: The new balance in line's currency.
        :param move_type:       The type of the move.
        :param currency:        The currency.
        :param taxes:           The applied taxes.
        :param price_subtotal:  The price_subtotal.
        :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
        '''
        # logging.info(f"Price Subtotal ------>:--------------> {price_subtotal}")
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        amount_currency *= sign

        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if not force_computation and currency.is_zero(amount_currency - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency, currency=currency, handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    amount_currency += tax_res['amount']
        
        discount_factor = 1 - (discount / 100.0)
        # fix_discount = fix_discount/quantity
        if amount_currency and discount_factor :
            # discount != 100%
            vals = {
                'quantity': quantity or 1.0,
                'price_unit': ((amount_currency) / discount_factor / (quantity or 1.0)),
            }
            # logging.info(f"Inside If 1Discount-------------->{vals}")
        elif amount_currency and not discount_factor:
            # discount == 100%
            vals = {
                'quantity': quantity or 1.0,
                'discount': 0.0,
                'price_unit': (amount_currency / (quantity or 1.0)),
            }
            # logging.info(f"Inside elif 1Discount-------------->{vals}")
            
        elif not discount_factor:
            # balance of line is 0, but discount  == 100% so we display the normal unit_price
            vals = {}
            # logging.info(f"Inside elif Not Discount-------------->{vals}")
        else:
            # balance is 0, so unit price is 0 as well
            vals = {'price_unit': 0.0}
            # logging.info(f"Inside else-------------->{vals}")
        return vals
    
    def _get_fields_onchange_balance(self, quantity=None, discount=None, amount_currency=None, move_type=None, currency=None, taxes=None, price_subtotal=None, force_computation=False):
        self.ensure_one()
        return self._get_fields_onchange_balance_model(
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            amount_currency=self.amount_currency if amount_currency is None else amount_currency,
            move_type=self.move_id.move_type if move_type is None else move_type,
            currency=(self.currency_id or self.move_id.currency_id) if currency is None else currency,
            taxes=self.tax_ids if taxes is None else taxes,
            price_subtotal=self.price_subtotal if price_subtotal is None else price_subtotal,
            # fix_discount=self.fix_discount if fix_discount is None else fix_discount,
            force_computation=force_computation,
        )
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount','tax_ids')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

            # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
            # company.
            currency_id = vals.get('currency_id') or move.company_id.currency_id.id
            if currency_id == move.company_id.currency_id.id:
                balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                vals.update({
                    'currency_id': currency_id,
                    'amount_currency': balance,
                })
            else:
                vals['amount_currency'] = vals.get('amount_currency', 0.0)

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    # logging.info(f"Price Unit form Create:--------------> {vals.get('price_unit', 0.0)}")
                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        # vals.get('fix_discount', 0.0),
                    ).get('price_subtotal', 0.0)
                    # logging.info(f"Price Unit form gptsm price_subtotal:--------------> {price_subtotal}")
                    
                    gfobm=vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        vals['amount_currency'],
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal,
                        # vals.get('fix_discount', 0.0),
                    ))
                    # logging.info(f"Price Unit form Create before update:--------------> {gfobm}")
                    
                    gptsm=vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        # vals.get('fix_discount', 0.0),
                    ))
                    # logging.info(f"GPTSM updated update:--------------> {gptsm}")
                    
                elif any(vals.get(field) for field in BUSINESS_FIELDS):                    
                    # logging.info(f"Price Unit form Create before update if Business Field:--------------> {vals.get('price_unit', 0.0)}")
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        # vals.get('fix_discount', 0.0),
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.move_type,
                        currency,
                        move.company_id,
                        move.date,
                    ))

        lines = super().create(vals_list) #------------------> Original Line of Code <---------------

        # Set the context for check_move_validity before creating the lines
        # lines = super(AMLFixDiscount, self.with_context(check_move_validity=False)).create(vals_list)

        moves = lines.mapped('move_id')
        if self._context.get('check_move_validity', True):
            moves._check_balanced()
        moves.filtered(lambda m: m.state == 'posted')._check_fiscalyear_lock_date()
        lines.filtered(lambda l: l.parent_state == 'posted')._check_tax_lock_date()
        moves._synchronize_business_models({'line_ids'})

        return lines
    
    
