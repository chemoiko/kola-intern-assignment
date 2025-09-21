
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

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            winner = order.partner_id
            if winner and order.rfq_vendor_ids:
                others = order.rfq_vendor_ids.filtered(lambda v: v.partner_id.id != winner.id)
                if others:
                    others.unlink()
        return res

class PurchaseRfqVendor(models.Model):
    _name = 'purchase.rfq.vendor'
    _description = 'RFQ Vendor'
    _order = 'sequence, id'

    rfq_id = fields.Many2one('purchase.order', string='RFQ', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier_rank', '>=', 0)])
    sequence = fields.Integer(string='Sequence', default=10)

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

    def _apply_won_side_effects(self):
        # Apply side-effects of a bid being marked as won without rewriting state again
        for bid in self:
            if not bid.rfq_id:
                continue
            other_bids = bid.rfq_id.bid_ids.filtered(lambda b: b.id != bid.id)
            if other_bids:
                other_bids.write({'state': 'lost'})
            link_model = self.env['purchase.rfq.vendor']
            if not bid.rfq_id.rfq_vendor_ids.filtered(lambda v: v.partner_id.id == bid.vendor_id.id):
                link_model.create({
                    'rfq_id': bid.rfq_id.id,
                    'partner_id': bid.vendor_id.id,
                })
            bid.rfq_id.partner_id = bid.vendor_id.id

    def action_set_won(self):
        # Approve selected bid(s) and show toast notification
        for bid in self:
            if not bid.rfq_id:
                continue
            if bid.state != 'won':
                bid.with_context(skip_won_hook=True).write({'state': 'won'})
            bid._apply_won_side_effects()

        # Show success toast using bus notification (no page reload needed)
        if len(self) == 1:
            bid = self[0]
            vendor_name = bid.vendor_id.display_name or 'Vendor'
            rfq_name = bid.rfq_id.name or 'RFQ'
            message = f"{vendor_name} selected as winner for {rfq_name}."
        else:
            message = "Selected bid(s) approved as winner."

        # Send notification via bus
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'simple_notification',
            {
                'title': 'Bid Approved',
                'message': message,
                'type': 'success',
            }
        )

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals and vals['state'] == 'won' and not self.env.context.get('skip_won_hook'):
            for rec in self.filtered(lambda r: r.state == 'won'):
                rec._apply_won_side_effects()
        return res

    def action_set_lost(self):
        for bid in self:
            if bid.state != 'lost':
                bid.write({'state': 'lost'})


