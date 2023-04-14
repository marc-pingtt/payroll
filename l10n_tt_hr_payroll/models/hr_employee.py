from odoo import api, fields, models
from datetime import date, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    bir_file_number = fields.Char('BIR File Number')
    nis_number = fields.Char('NIS Number')
    age = fields.Integer(string="Age", compute="_compute_age")
    birthday = fields.Date(
        'Date of Birth', required=True)
    address_home_id = fields.Many2one(
        'res.partner', 'Address', help='Enter here the private address of the employee, not the one linked to your company.',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=True)

    @api.depends('birthday')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.birthday:
                rec.age = today.year - rec.birthday.year - \
                    ((today.month, today.day) <
                     (rec.birthday.month, rec.birthday.day))
            else:
                rec.age = 0
