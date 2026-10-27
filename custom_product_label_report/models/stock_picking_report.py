from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def get_report_values(self, docids, data=None):
    #     docs = self.env['stock.picking'].browse(docids)
    #     products = docs.move_ids_without_package
    #     data = []
    #     for product in products:
    #         product = product.name
    #         data.append(product)
    #     total_quantity = sum(len(qtys) for qtys in data)
    #     rows = 100
    #     columns = 100
    #     page_numbers = (total_quantity - 1) // (rows * columns) + 1
    #     return {'docs': docs,'page_numbers':1,'product':products}
