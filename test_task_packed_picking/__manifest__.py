"""Manifest"""
{
    'name': 'Test Task Packed Picking',
    'version': '16.0.1.0.0',
    'summary': 'Custom module to create a packed picking',
    'author': 'Nikola Vlavcheski',
    'depends': ['stock'],
    'data': [
        'views/pack_products_wizard_view.xml',
        'views/menu_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True
}
