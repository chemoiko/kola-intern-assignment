
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_ids = fields.Many2many(
        'res.partner',
        'purchase_order_vendor_rel',   # relation table name
        'order_id',                    # column linking to purchase.order
        'partner_id',                  # column linking to res.partner
        string='Vendors',
        domain=[('supplier_rank', '>', 0)]
    )


