
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfq_vendor_ids = fields.One2many(
        'purchase.rfq.vendor',
        'rfq_id',
        string='Vendors'
    )
    bid_ids = fields.One2many(
        'purchase.rfq.bid',
        'rfq_id',
        string='Bids'
    )

class PurchaseRfqVendor(models.Model):
    _name = 'purchase.rfq.vendor'
    _description = 'RFQ Vendor'

    rfq_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier_rank', '>=', 0)])

    _sql_constraints = [
        ('uniq_rfq_partner', 'unique(rfq_id, partner_id)', 'This vendor is already linked to this RFQ.')
    ]

class PurchaseRfqBid(models.Model):
    _name = 'purchase.rfq.bid'
    _description = 'RFQ Bid'

    rfq_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier_rank', '>=', 0)])
    price_total = fields.Monetary(string='Offer')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    note = fields.Text()
    state = fields.Selection([('draft','Draft'),('submitted','Submitted'),('won','Won'),('lost','Lost')], default='draft')

    _sql_constraints = [
        ('uniq_rfq_vendor', 'unique(rfq_id, vendor_id)', 'This vendor already has a bid on this RFQ.')
    ]


