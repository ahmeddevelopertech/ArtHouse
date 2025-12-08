from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPickingPartialLine(models.Model):
    _name = 'stock.picking.partial.line'
    _description = 'Picking Partial Delivery Line'

    picking_id = fields.Many2one('stock.picking', string='Picking', required=True, ondelete='cascade')
    move_id = fields.Many2one('stock.move', string='Related Move', required=True)
    product_id = fields.Many2one('product.product', string='Product', related='move_id.product_id', store=True)
    ordered_qty = fields.Float(string='Ordered Qty', related='move_id.product_uom_qty', store=True)
    qty_to_deliver = fields.Float(string='Qty to deliver')

    @api.onchange('qty_to_deliver')
    def _onchange_qty_to_deliver(self):
        for rec in self:
            if rec.qty_to_deliver < 0:
                rec.qty_to_deliver = 0
            if rec.qty_to_deliver > rec.ordered_qty:
                # allow user to enter more, but warn (optional)
                pass


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('partial', 'Partial Delivery')])

    partial_line_ids = fields.One2many('stock.picking.partial.line', 'picking_id', string='Partial Delivery Lines')

    def _prepare_partial_lines(self):
        lines = []
        for move in self.move_ids_without_package:
            lines.append((0, 0, {
                'move_id': move.id,
                'qty_to_deliver': 0.0,
            }))
        return lines

    def action_open_partial_tab(self):
        for picking in self:
            if not picking.partial_line_ids:
                picking.partial_line_ids = picking._prepare_partial_lines()
        return True

    def action_apply_partial_delivery(self):
        """Apply the qty_to_deliver values to stock.move.line(s) as quantity (instead of qty_done)."""
        StockMoveLine = self.env['stock.move.line']
        for picking in self:
            for pl in picking.partial_line_ids:
                move = pl.move_id
                qty = float(pl.qty_to_deliver or 0.0)
                if qty <= 0:
                    continue

                # find existing move_line
                ml = move.move_line_ids.filtered(lambda l:
                                                 l.product_id == move.product_id and
                                                 l.location_id == move.location_id and
                                                 l.location_dest_id == move.location_dest_id)
                if ml:
                    ml[0].quantity = float(ml[0].quantity or 0.0) + qty
                else:
                    vals = {
                        'move_id': move.id,
                        'picking_id': picking.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'quantity': qty,  # ✅ Odoo 17 uses "quantity"
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                    }
                    StockMoveLine.create(vals)

        # update picking state
        for picking in self:
            total = sum(picking.move_ids_without_package.mapped('product_uom_qty'))
            done = sum(picking.move_ids_without_package.mapped(lambda m: sum(m.move_line_ids.mapped('quantity'))))
            if 0 < done < total:
                picking.state = 'partial'
            elif done >= total:
                picking.state = 'done'
        return True

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            total = sum(picking.move_ids_without_package.mapped('product_uom_qty'))
            done = sum(picking.move_ids_without_package.mapped(
                lambda m: sum(m.move_line_ids.mapped('quantity'))))
            if 0 < done < total:
                picking.state = 'partial'
        return res
