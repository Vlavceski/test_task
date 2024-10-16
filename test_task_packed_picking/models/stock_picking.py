"""Defines the logic for packed picking in stock.picking model."""
from odoo import models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    """Extends stock.picking to create packed pickings."""
    _inherit = 'stock.picking'

    def _create_packed_picking(self, operation_type, stock_move_data, owner=None,
                               location=None, location_dest_id=None, package_name=None,
                               create_lots=False, set_ready=False):
        """Create a picking and put its product into a package.

        Args:
            operation_type (stock.picking.type): Operation type
            stock_move_data (list of tuples): [(product_id, qty_done, serial)]
            owner (res.partner, optional): Owner of the product
            location (stock.location, optional): Source location
            location_dest_id (stock.location, optional): Destination location
            package_name (str, optional): Name of the package
            create_lots (bool, optional): Whether to create lots
            set_ready (bool, optional): Whether to set picking to ready

        Returns:
            stock.picking: Created picking
        """
        # Default to the operation type locations if not specified
        location = location or operation_type.default_location_src_id
        location_dest_id = location_dest_id or operation_type.default_location_dest_id

        picking_vals = {
            'picking_type_id': operation_type.id,
            'location_id': location.id,
            'location_dest_id': location_dest_id.id,
            'partner_id': owner.id if owner else None,
        }

        picking = self.env['stock.picking'].create(picking_vals)

        for move_data in stock_move_data:
            product_id, qty_done, serial = move_data
            product = self.env['product.product'].search([('id', '=', product_id)], limit=1)

            if not product:
                raise ValidationError(f"Product with ID {product_id} does not exist.")

            move_vals = {
                'picking_id': picking.id,
                'product_id': product.id,
                'product_uom_qty': qty_done,
                'product_uom': product.uom_id.id,
                'location_id': location.id,
                'location_dest_id': location_dest_id.id,
                'name': product.name,
            }

            move = self.env['stock.move'].create(move_vals)
            move.write({'quantity_done': qty_done})

            # Create lots if required
            if create_lots and serial:
                self.env['stock.lot'].create({
                    'product_id': product_id,
                    'name': serial
                })

        # If package name is provided, create a package
        if package_name:
            package = self.env['stock.quant.package'].create({'name': package_name})
            picking.move_line_ids.write({'result_package_id': package.id})

        # If set_ready is True, confirm and assign picking
        if set_ready:
            picking.action_confirm()
            picking.action_assign()

        return picking
