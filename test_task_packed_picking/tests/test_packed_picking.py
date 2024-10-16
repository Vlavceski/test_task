"""Unit tests for packed picking in stock.picking model."""
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPackedPicking(TransactionCase):

    def setUp(self):
        """Set up test data for packed picking tests."""
        super().setUp()

        self.location_src = self.env['stock.location'].create({
            'name': 'Source Location'
        })
        self.location_dest = self.env['stock.location'].create({
            'name': 'Destination Location'
        })

        self.operation_type = self.env['stock.picking.type'].create({
            'name': 'Test Operation Type',
            'sequence_code': 'TEST_OP',
            'code': 'outgoing',
            'default_location_src_id': self.location_src.id,
            'default_location_dest_id': self.location_dest.id,
            'use_create_lots': True,
            'use_existing_lots': True,
            'reservation_method': 'at_confirm',
            'create_backorder': 'ask'
        })

        self.product = self.env['product.product'].create({
            'name': 'TEST Product 1',
            'type': 'product'
        })

        self.owner = self.env['res.partner'].create({
            'name': 'Test Owner'
        })

    def test_create_packed_picking(self):
        stock_move_data = [(self.product.id, 16.0, None)]

        picking = self.env['stock.picking']._create_packed_picking(
            self.operation_type, stock_move_data
        )

        self.assertTrue(picking, "Picking was not created")
        self.assertEqual(picking.state, 'draft', "Picking state is not 'draft'")
        self.assertEqual(picking.picking_type_id, self.operation_type, "Picking type mismatch")
        self.assertEqual(picking.location_id, self.location_src, "Source location mismatch")
        self.assertEqual(picking.location_dest_id, self.location_dest, "Destination location mismatch")

    def test_create_packed_picking_with_lots(self):
        """Test picking creation with serial numbers"""
        stock_move_data = [
            (self.product.id, 10.0, 'TEST_SERIAL_001'),
            (self.product.id, 5.0, 'TEST_SERIAL_002')
        ]

        picking = self.env['stock.picking']._create_packed_picking(
            self.operation_type, stock_move_data, create_lots=True
        )

        self.assertEqual(len(picking.move_line_ids), 2, "There should be 2 stock moves")

        lots = self.env['stock.lot'].search([('name', 'in', ['TEST_SERIAL_001', 'TEST_SERIAL_002'])])
        self.assertEqual(len(lots), 2, "Lots were not created correctly")

    def test_create_packed_picking_with_owner(self):
        """Test picking creation with owner"""
        stock_move_data = [(self.product.id, 16.0, None)]

        picking = self.env['stock.picking']._create_packed_picking(
            self.operation_type, stock_move_data, owner=self.owner
        )

        self.assertEqual(picking.partner_id, self.owner, "Owner was not set correctly")

    def test_create_packed_picking_with_package(self):
        """Test picking creation with package"""
        stock_move_data = [(self.product.id, 16.0, None)]
        package_name = 'TEST_PACKAGE_001'

        picking = self.env['stock.picking']._create_packed_picking(
            self.operation_type, stock_move_data, package_name=package_name
        )

        package = self.env['stock.quant.package'].search([('name', '=', package_name)])
        self.assertTrue(package, "Package was not created")
        self.assertEqual(picking.move_line_ids[0].result_package_id, package, "Package was not assigned to move lines")

    def test_create_packed_picking_set_ready(self):
        """Test picking creation with the 'set_ready'"""
        stock_move_data = [(self.product.id, 16.0, None)]

        picking = self.env['stock.picking']._create_packed_picking(
            self.operation_type, stock_move_data, set_ready=True
        )

        self.assertEqual(picking.state, 'confirmed', "Picking state should be 'confirmed' when set_ready is True")

    def test_create_packed_picking_invalid_product(self):
        """Test picking creation with invalid product."""
        invalid_product_id = 99999
        stock_move_data = [(invalid_product_id, 16.0, None)]

        with self.assertRaises(ValidationError):
            self.env['stock.picking']._create_packed_picking(
                self.operation_type, stock_move_data
            )
