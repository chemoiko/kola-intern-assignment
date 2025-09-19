
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_ids = fields.Many2many('res.partner','purchase_order_vendor_rel','order_id','partner_id', string='Vendors')


