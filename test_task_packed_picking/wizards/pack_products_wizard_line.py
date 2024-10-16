from odoo import models, fields


class PackProductsWizardLine(models.TransientModel):
    _name = 'pack.products.wizard.line'
    _description = 'Pack Products Wizard Line'

    wizard_id = fields.Many2one('pack.products.wizard')
    product_id = fields.Many2one('product.product', required=True)
    qty_done = fields.Float(required=True)
    serial = fields.Char()
