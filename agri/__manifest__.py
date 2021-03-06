# Copyright 2020 Agrista GmbH (https://agrista.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name":
    "Agri",
    "summary":
    "Agriculture base module",
    "website":
    "https://github.com/agrista/odoo-agri",
    "category":
    "Operations/Inventory",
    "version":
    "0.1.0",
    "sequence":
    1,
    "author":
    "Agrista GmbH",
    "license":
    "AGPL-3",
    "description":
    "Agriculture base module",
    "depends": ['base', 'uom', 'product'],
    "data": [
        'security/agri_security.xml',
        'security/ir.model.access.csv',
        'data/uom_data.xml',
        'data/product_data.xml',
        # 'data/agri.budget.template.csv',
        # 'data/agri.budget.template.line.csv',
        'data/agri_crop_data.xml',
        'data/agri_irrigation_data.xml',
        'data/agri.land.use.csv',
        'data/agri_soil_data.xml',
        'data/agri_terrain_data.xml',
        'data/agri_water_data.xml',
        'data/decimal_precision_data.xml',
        'views/agri_views.xml',
        'views/assets.xml',
        'views/ir_attachment_views.xml',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
    ],
    "demo": [],
    "application":
    True,
    "installable":
    True,
    "auto_install":
    False,
}
