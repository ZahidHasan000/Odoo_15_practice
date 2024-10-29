from odoo import models
import json


class SaleOrderXlsx(models.AbstractModel):
    _name = 'report.meta_sale_order_xlsx.report_sale_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Sale Order Xlsx Report"

    def generate_xlsx_report(self, workbook, data, sale):
        for obj in sale:
            # Calculate the width of the column based on the object name length
            name_length = len(obj.name)
            column_width = max(10, name_length)  # Set a minimum width of 10

            sheet = workbook.add_worksheet(obj.name)
            bold = workbook.add_format({'bold': True})
            wrap = workbook.add_format({'text_wrap': True})
            date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
            align_center = workbook.add_format({'align': 'center'})

            # Set the column width dynamically based on the name length
            sheet.set_column(8, 8, column_width)

            row = 5
            col = 8
            sheet.write(row, col, 'Order Date', bold)
            col += 1
            sheet.write(row, col, obj.date_order, date_format)
            row += 1
            col -= 1
            sheet.write(row, col, 'Payment Terms', bold)
            col += 1
            sheet.write(row, col, obj.payment_term_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'Invoice Status', bold)
            col += 1
            sheet.write(row, col, obj.invoice_status)
            row = 1
            col = 1
            sheet.merge_range(row, col, row, col + 8, 'Sale Order', align_center)
            row += 2
            col = 1
            sheet.write(row, col, obj.name, bold)
            row += 2
            sheet.write(row, col, 'Customer', bold)
            col += 1
            sheet.write(row, col, obj.partner_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'Salesperson', bold)
            col += 1
            sheet.write(row, col, obj.user_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'State', bold)
            col += 1
            sheet.write(row, col, obj.state)
            if obj.origin:
                row += 1
                col -= 1
                sheet.write(row, col, 'Source Document', bold)
                col += 1
                sheet.write(row, col, obj.origin)
            row += 2
            col = 1
            sheet.write(row, col, 'Product', bold)
            col += 1
            sheet.write(row, col, 'Description', bold)
            col += 1
            sheet.write(row, col, 'Quantity', bold)
            col += 1
            sheet.write(row, col, 'Delivered', bold)
            col += 1
            sheet.write(row, col, 'Invoiced', bold)
            col += 1
            sheet.write(row, col, 'UoM', bold)
            col += 1
            sheet.write(row, col, 'Unit Price', bold)
            col += 1
            sheet.write(row, col, 'Taxes', bold)
            col += 1
            sheet.write(row, col, 'Subtotal', bold)
            row += 1
            col = 1
            tx_list = []
            for record in obj.order_line:
                for tx in record.tax_id:
                    tx_list.append(tx.name)
                sheet.write(row, col, record.product_id.name)
                col += 1
                sheet.write(row, col, record.name, wrap)
                col += 1
                sheet.write(row, col, record.product_uom_qty)
                col += 1
                sheet.write(row, col, record.qty_delivered)
                col += 1
                sheet.write(row, col, record.qty_invoiced)
                col += 1
                sheet.write(row, col, record.product_uom.name)
                col += 1
                sheet.write(row, col, record.price_unit)
                col += 1
                sheet.write(row, col, ', '.join(tx_list))
                col += 1
                sheet.write(row, col, record.price_subtotal)
                col = 1
                row += 1
                tx_list.clear()
            row += 1
            col = 8
            sheet.write(row, col, 'Untaxed Amount:', bold)
            col += 1
            sheet.write(row, col, json.loads(obj.tax_totals_json).get('amount_untaxed'))
            row += 1
            col = 8
            if json.loads(obj.tax_totals_json).get('groups_by_subtotal').get('Untaxed Amount'):
                for rec in json.loads(obj.tax_totals_json).get('groups_by_subtotal').get('Untaxed Amount'):
                    sheet.write(row, col, rec.get('tax_group_name'))
                    col += 1
                    sheet.write(row, col, rec.get('tax_group_amount'))
                    row += 1
                    col -= 1
            col = 8
            sheet.write(row, col, 'Total:')
            col += 1
            sheet.write(row, col, json.loads(obj.tax_totals_json).get('amount_total'))
