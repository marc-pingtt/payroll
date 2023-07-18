from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import calendar
from decimal import Decimal
from dateutil.relativedelta import relativedelta


class NisReportWizard(models.TransientModel):
    _name = 'nis.ni184.report.wizard'
    _description = 'NIS Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    date_start = fields.Date('Start Period', required=True)
    date_end = fields.Date('End Period')

    @api.onchange("date_start")
    def compute_date_end(self):
        if (self.date_start != False):
            last_day = calendar.monthrange(
                self.date_start.year, self.date_start.month)[1]
            self.date_end = date(
                self.date_start.year, self.date_start.month, last_day)

    all_employees = fields.Boolean('All Employees ?')

    def print(self):
        data = {'employee_ids': self.employee_ids.ids,
                'date_start': self.date_start, 'date_end': self.date_end,
                'all_employees': self.all_employees}
        return self.env.ref('l10n_tt_hr_payroll.nis_ni184_report_wizard_action').report_action(self.employee_ids, data=data)
