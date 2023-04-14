from odoo import api, fields, models, _


class TD4Report(models.AbstractModel):
    _name = 'report.payroll_reports.report_employee'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.employee'].browse(data['context']['active_ids'])
        print(self.env['hr.employee'].browse(data['context']['active_ids']), 'docs')
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': docs,
            'data': data,
        }
        