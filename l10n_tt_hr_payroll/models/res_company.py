from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    bir_file_number = fields.Char('BIR File Number')
    paye_file_number = fields.Char('PAYE File Number')
    health_surcharge_account_number = fields.Char(
        'Health Surcharge Account Number')
