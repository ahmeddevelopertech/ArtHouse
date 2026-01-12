from odoo import api, models, _, fields
import logging
import traceback
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    ManufacturingNote = fields.Text('Manufacturing Note')
    Files = fields.Binary('Files' )

    manufacturing_status = fields.Selection(
        [('draft', 'Draft'), ('sent_to_manufacturing', 'Sent to Manufacturing')],
        string='Manufacturing Status',
        default='draft',
        readonly=True,
        help="Tracks whether this invoice has been sent to manufacturing"
    )

    def action_send_to_factory(self):
        # Process only customer invoices
        for invoice in self.filtered(lambda inv: inv.move_type == 'out_invoice'):
            _logger.info("Processing customer invoice: %s", invoice.name)
            # Avoid duplicate MOs by invoice origin
            existing = self.env['mrp.production'].search([('origin', '=', invoice.name)])
            if not existing:
                self._create_manufacturing_orders(invoice)

    def _create_manufacturing_orders(self, invoice):
        """Create one manufacturing order for each invoice line with full details."""
        _logger.info("Creating MOs for invoice: %s", invoice.name)

        # Create a single procurement group for all MOs
        procurement_group = self.env['procurement.group'].create({
            'name': f"MO from Invoice {invoice.name}",
            'partner_id': invoice.partner_id.id,
            'move_type': 'direct',
        })
        _logger.info("Procurement group created: %s", procurement_group.name)

        # Loop through each product line
        lines = invoice.invoice_line_ids.filtered(lambda l: l.product_id.type in ['product', 'consu'])
        for line in lines:
            product = line.product_id
            qty = line.quantity

            if line.name == "discount":
                continue
            if line.name == "Standard delivery":
                continue

            # Find BOM data
            bom_data = self.env['mrp.bom']._bom_find(product)
            bom = bom_data.get('bom') if bom_data else False
            if not bom:
                _logger.warning("No BOM found for %s (invoice %s), skipping", product.display_name, invoice.name)

            # Prepare MO values including invoice and client
            mo_vals = {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom_id': product.uom_id.id,
                'origin': invoice.name,
                'quotation_id': invoice.id,
                'client_name': invoice.partner_id.id,
                'company_id': invoice.company_id.id,
                'date_start': invoice.delivery_date,
                'procurement_group_id': procurement_group.id,
                'BranchFile': invoice.Files,
                'ManufacturingNote': invoice.ManufacturingNote+" "+line.name,
                'location_src_id': self.env['stock.location']
                .search([('usage', '=', 'internal'), ('company_id', '=', invoice.company_id.id)], limit=1).id,
                'location_dest_id': self.env['stock.location']
                .search([('usage', '=', 'production'), ('company_id', '=', invoice.company_id.id)], limit=1).id,
            }
            _logger.info("MO values for %s: %s", product.display_name, mo_vals)

            try:
                mo = self.env['mrp.production'].create(mo_vals)
                _logger.info("Created MO %s for product %s", mo.name, product.display_name)

                # Link invoice attachments if any
                if invoice.attachment_ids:
                    mo.write({'attachment_ids': [(6, 0, invoice.attachment_ids.ids)]})

                self.write({'manufacturing_status': 'sent_to_manufacturing'})
                _logger.info("Confirmed MO %s", mo.name)


            except Exception as e:
                raise ValidationError(f"Error processing MO for invoice {invoice.name}: {e}")
                _logger.error(
                    "Failed to create MO for %s: %s\n%s", product.display_name, str(e), traceback.format_exc()
                )
                continue

    @api.constrains('delivery_date', 'move_type')
    def _check_delivery_date(self):
        for record in self:
            if record.move_type in ['out_invoice'] and not record.delivery_date:
                raise ValidationError("Delivery date is required for customer invoices and refunds")