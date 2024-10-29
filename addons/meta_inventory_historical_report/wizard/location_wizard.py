from odoo import fields, models


class OrderWizardReport(models.TransientModel):
    _name = 'location.wizard'

    location_id = fields.Many2one('stock.location', string="Location",
                                  domain=["&", ('usage', '=', 'internal'), ('location_id.usage', '=', 'view')])
    # location_id = fields.Many2one('stock.location', string="Location")
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)

    product_history = fields.Selection([
        ('in', 'In Product'),
        ('out', 'Out Product')
    ], string='Product History')

    def product_print_report(self):
        self._cr.execute('TRUNCATE TABLE location_in_history_data')
        self._cr.execute('TRUNCATE TABLE location_out_history_data')

        if self.product_history == 'in':
            # Fetch the data for In Product report
            date_range_in_moves = self.env['stock.move.line'].sudo().search([
                ('date', '>', self.start_date),
                ('date', '<', self.end_date),
                ('state', '=', 'done'),
                ('location_dest_id', '=', self.location_id.id)
            ])
            for item in date_range_in_moves:
                if item.qty_done > 0:
                    self.env['location.in.history.data'].sudo().create({
                        'product_id': item.product_id.id,
                        'date': item.date,
                        'quantity': item.qty_done,
                        'source_location': item.location_id.id,
                        'destination_location': item.location_dest_id.id
                    })

            search_product_in_data = self.env['location.in.history.data'].sudo().search_read([])

            data = {
                'form_data': self.read()[0],
                'product_item_in': search_product_in_data,
            }
            return self.env.ref('meta_inventory_historical_report.action_product_report_by_location_in').report_action(
                [], data=data)

        elif self.product_history == 'out':
            # Fetch the data for Out Product report
            date_range_out_moves = self.env['stock.move.line'].sudo().search([
                ('date', '>', self.start_date),
                ('date', '<', self.end_date),
                ('state', '=', 'done'),
                ('location_id', '=', self.location_id.id)
            ])
            for item in date_range_out_moves:
                if item.qty_done > 0:
                    self.env['location.out.history.data'].sudo().create({
                        'product_id': item.product_id.id,
                        'date': item.date,
                        'quantity': item.qty_done,
                        'source_location': item.location_id.id,
                        'destination_location': item.location_dest_id.id
                    })

            search_product_out_data = self.env['location.out.history.data'].sudo().search_read([])

            data = {
                'form_data': self.read()[0],
                'product_item_out': search_product_out_data,
            }
            return self.env.ref('meta_inventory_historical_report.action_product_report_by_location_out').report_action(
                [], data=data)
