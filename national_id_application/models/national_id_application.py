from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class NationalIDApplication(models.Model):
    _name = 'national.id.application'
    _description = 'National ID Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(string="Full Name", required=True)
    # Optional granular name parts for website form
    dob = fields.Date(string="Date of Birth", required=True)
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], string="Gender", required=True)
    address = fields.Char(string="Address", required=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ], string="Marital Status")
    nationality = fields.Selection([
        ('ugandan', 'Ugandan'),
        ('kenyan', 'Kenyan'),
        ('tanzanian', 'Tanzanian'),
        ('rwandan', 'Rwandan'),
        ('burundian', 'Burundian'),
        ('south_sudanian', 'South Sudanese'),
        ('drc', 'DR Congolese'),
        ('other', 'Other'),
    ], string="Nationality")
    phone = fields.Char(string="Phone Number", required=True)
    next_of_kin = fields.Char(string="Next of Kin Name")
    next_of_kin_phone = fields.Char(string="Next of Kin Phone")
    email = fields.Char(string="Email", required=True)
    photo = fields.Image(string="Photo", max_width=1024, max_height=1024)
    lc_letter = fields.Binary(string="Letter of Consent")
    tracking_number = fields.Char(
        string="Tracking Number", readonly=True, copy=False, default="New")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('senior_approved', 'Senior Approved'),
        ('final_approved', 'Final Approved'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True, string="Status")
    application_date = fields.Datetime(
        string="Application Date", default=fields.Datetime.now)
    # Verification fields (custom workflow)
    verified_status = fields.Boolean(string="Verified Status")
    verification_result = fields.Selection([
        ('pending', 'Pending'),
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], string="Verification Result", default='pending')
    name_match = fields.Boolean(string="Name Match")
    address_match = fields.Boolean(string="Address Match")
    phone_confirmed = fields.Boolean(string="Phone Confirmed")
    email_confirmed = fields.Boolean(string="Email Confirmed")
    photo_quality = fields.Selection([
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
        ('poor', 'Poor')
    ], string="Photo Quality")
    lc_present = fields.Boolean(string="LC Letter Present")
    lc_valid = fields.Boolean(string="LC Letter Valid")
    verification_notes = fields.Text(
        string="Verification Notes", tracking=True)
    senior_approver_notes = fields.Text(
        string="Senior Approver Notes", tracking=True)
    final_approver_notes = fields.Text(
        string="Final Approver Notes", tracking=True)
    verified_by = fields.Many2one(
        'res.users', string="Last Action By", readonly=True, copy=False)
    verified_on = fields.Datetime(
        string="Last Action On", readonly=True, copy=False)

    @api.model
    def _get_default_tracking_number(self):
        return self.env["ir.sequence"].next_by_code("national.id.application")

    @api.model
    def create(self, vals):
        # Simple name normalization
        if vals.get('name'):
            vals['name'] = vals['name'].strip().title()
        if vals.get('next_of_kin'):
            vals['next_of_kin'] = vals['next_of_kin'].strip().title()

        # Generate tracking number
        if vals.get('tracking_number', 'New') == 'New':
            vals['tracking_number'] = self._get_default_tracking_number()

        record = super(NationalIDApplication, self).create(vals)
        # Send acknowledgment email
        record.send_ack_email()

        return record

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({
            "state": "draft",
            "tracking_number": self._get_default_tracking_number()
        })
        return super(NationalIDApplication, self).copy(default)

    def send_ack_email(self):
        template = self.env.ref(
            'national_id_application.national_ack_email_template')
        template.send_mail(self.id, force_send=True)

    def action_verify(self):
        self.state = 'verified'
        self.verified_status = True
        self.verification_result = 'pass' if (
            self.name_match and self.address_match) else self.verification_result or 'pending'
        self.verified_by = self.env.user
        self.verified_on = fields.Datetime.now()
        tmpl = self.env.ref(
            'national_id_application.template_verification_done', raise_if_not_found=False)
        if tmpl:
            tmpl.send_mail(self.id, force_send=True)

    def action_senior_approve(self):
        self.state = 'senior_approved'
        self.verified_by = self.env.user
        self.verified_on = fields.Datetime.now()
        tmpl = self.env.ref(
            'national_id_application.template_senior_done', raise_if_not_found=False)
        if tmpl:
            tmpl.send_mail(self.id, force_send=True)

    def action_final_approve(self):
        self.state = 'final_approved'
        self.verified_by = self.env.user
        self.verified_on = fields.Datetime.now()
        tmpl = self.env.ref(
            'national_id_application.template_final_done', raise_if_not_found=False)
        if tmpl:
            tmpl.send_mail(self.id, force_send=True)

    def action_reject(self):
        self.state = 'rejected'

    def action_view_photo(self):
        self.ensure_one()
        if not self.photo:
            raise UserError("No photo uploaded.")
        url = f"/web/image?model={self._name}&id={self.id}&field=photo"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_view_lc_letter(self):
        self.ensure_one()
        if not self.lc_letter:
            raise UserError("No letter of consent uploaded.")
        url = f"/web/content?model={self._name}&id={self.id}&field=lc_letter&filename=lc_letter"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
