from odoo import models, fields



class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"


    title = fields.Char(string="Title")
    postcode = fields.Char(string="Postcode")
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Float(string="Living Area (sqm)")
    expected_price = fields.Float(string="Expected Price")
    selling_price = fields.Float(string="Selling Price")
    available_from = fields.Date(string="Available From")
    description = fields.Char(string="Description")
    facades = fields.Integer(string="facades")
    garage = fields.Boolean(string="garage")
    garden = fields.Boolean(string="Garden ")
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection(
        [
            ('north', 'North'), ('south', 'South'),
             ('east', 'East'), ('west', 'West')],
        string="Garden Orientation"
        
        )

