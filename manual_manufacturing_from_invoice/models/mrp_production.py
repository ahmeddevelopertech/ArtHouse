from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class Manufacturing(models.Model):
    _inherit = 'mrp.production'
    ManufacturingNote = fields.Text('Manufacturing Note' , readonly=True)
    BranchFile = fields.Binary('Files', readonly=True)

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('type', 'in', ['product', 'consu'])]",
        required=True,  # Revert to required, using placeholder
        help='Main product or placeholder for multi-product orders.'
    )
    product_line_ids = fields.One2many(
        'mrp.production.product.line',
        'production_id',
        string='Products',
        domain="[('type', 'in', ['product', 'consu'])]",
        required=True,
        help='Products to manufacture with quantities.'
    )
    bom_ids = fields.Many2many(
        'mrp.bom',
        string='Bills of Materials',
        readonly=True,
        help='BOMs associated with the products in this manufacturing order.'
    )
    Files = fields.Many2many('ir.attachment', string='Files')
    quotation_id = fields.Many2one('account.move', string='Invoice Number')
    client_name = fields.Many2one('res.partner', string='Client')

    @api.model
    def create(self, vals):
        """Override create to ensure consistency."""
        _logger.info("Entering create with vals: %s", vals)
        record = super(Manufacturing, self).create(vals)
        _logger.info("Created record with product_id=%s, product_uom_id=%s", record.product_id.id, record.product_uom_id.id)
        return record

    def _manually_set_boms_and_components(self):
        """Manually set BOMs and components post-creation."""
        _logger.info("Manually setting BOMs and components for order: %s", self.name)
        if not self.product_line_ids:
            self.move_raw_ids = [(5, 0, 0)]
            return

        bom_ids = []
        component_lines = []
        for line in self.product_line_ids:
            bom = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('product_id', 'in', [False, line.product_id.id])
            ], limit=1)
            if bom:
                bom_ids.append(bom.id)
                _logger.info("Found BOM for %s: %s", line.product_id.name, bom.display_name)
                for bom_line in bom.bom_line_ids:
                    component_lines.append((0, 0, {
                        'name': bom_line.product_id.name,
                        'product_id': bom_line.product_id.id,
                        'product_uom_qty': bom_line.product_qty * line.quantity,
                        'product_uom': bom_line.product_uom_id.id,
                        'location_id': self.location_src_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'state': 'draft',
                        'raw_material_production_id': self.id,
                        'group_id': self.procurement_group_id.id if self.procurement_group_id else False,
                    }))
            else:
                _logger.warning("No BOM found for product: %s", line.product_id.name)

        self.write({
            'bom_ids': [(6, 0, bom_ids)],
            'move_raw_ids': [(5, 0, 0)] + component_lines if component_lines else [(5, 0, 0)]
        })
        _logger.info("BOMs and components set for order: %s", self.name)

    @api.onchange('product_line_ids', 'bom_ids')
    def _onchange_product_line_ids_and_boms(self):
        """Fallback onchange for manual edits."""
        self._manually_set_boms_and_components()

class MrpProductionProductLine(models.Model):
    _name = 'mrp.production.product.line'
    _description = 'Product Lines for Manufacturing'

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('type', 'in', ['product', 'consu'])]",
        required=True
    )
    quantity = fields.Float(string='Quantity', default=1.0, required=True)