from odoo import models, fields, api, _
import io
import json
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
from odoo.tools import date_utils
import base64

class PiConsumptionReportWizard(models.TransientModel):
    _name = 'pi.consumption.report.wizard'
    _description = 'Consumption Report Wizard'

    date_from = fields.Date('Date From', required=True, default=fields.Date.context_today)
    date_to = fields.Date('Date To', required=True, default=fields.Date.context_today)
    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('File Name')

    def action_get_report(self):
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
        return {
            'name': _('Daily Consumption Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'pi.consumption.report',
            'view_mode': 'tree,pivot',
            'domain': domain,
            'context': {'search_default_group_by_date': 1},
        }

    def action_export_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Daily Consumption')
        
        # Styles
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        default_format = workbook.add_format({'border': 1})
        
        # Headers
        headers = ['Date', 'Source', 'Product', 'Product Category', 'UOM', 'Consume Qty']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)
            sheet.set_column(col, col, 20)
            
        # Data
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
        records = self.env['pi.consumption.report'].search(domain, order='date asc')
        
        row = 1
        for rec in records:
            sheet.write(row, 0, rec.date, date_format)
            sheet.write(row, 1, rec.source or '', default_format)
            sheet.write(row, 2, rec.product_id.display_name or '', default_format)
            sheet.write(row, 3, rec.category_id.name or '', default_format)
            sheet.write(row, 4, rec.uom_id.name or '', default_format)
            sheet.write(row, 5, rec.quantity or 0.0, default_format)
            row += 1
            
        workbook.close()
        output.seek(0)
        
        file_data = base64.b64encode(output.read())
        output.close()
        
        self.write({
            'excel_file': file_data,
            'file_name': f'Daily_Consumption_Report_{self.date_from}_to_{self.date_to}.xlsx'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pi.consumption.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
