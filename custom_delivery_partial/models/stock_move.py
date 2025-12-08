from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'


    remaining_qty = fields.Float(
    string='Remaining Qty',
    compute='_compute_remaining_qty',
    store=False
    )


    def _compute_remaining_qty(self):
        for move in self:
             # product_uom_qty is the ordered/expected quantity
            done = sum(move.move_line_ids.mapped('qty_done'))
            move.remaining_qty = float(move.product_uom_qty - done)