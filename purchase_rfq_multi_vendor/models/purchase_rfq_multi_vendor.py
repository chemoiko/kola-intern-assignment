
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfq_vendor_ids = fields.One2many(
        'purchase.rfq.vendor',
        'rfq_id',
        string='Vendors'
    )

class PurchaseRfqVendor(models.Model):
    _name = 'purchase.rfq.vendor'
    _description = 'RFQ Vendor'

    rfq_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier_rank', '>=', 0)])

    _sql_constraints = [
        ('uniq_rfq_partner', 'unique(rfq_id, partner_id)', 'This vendor is already linked to this RFQ.')
    ]


