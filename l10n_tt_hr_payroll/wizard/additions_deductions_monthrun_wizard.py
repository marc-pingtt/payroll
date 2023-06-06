from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import calendar
from decimal import Decimal
class additionsReportWizard(models.TransientModel):
    _name = "additions.report.wizard"
    _description = "Addition Report"
    report_period_start = fields.Date("Report Period Start", required=True)
    report_period_end = fields.Date("Report Period End")
    @api.onchange("report_period_start")
    def compute_report_period_end(self):
        if (self.report_period_start != False):
            last_day = calendar.monthrange(
                self.report_period_start.year, self.report_period_start.month)[1]
            self.report_period_end = date(
                self.report_period_start.year, self.report_period_start.month, last_day)
    def payslip_search(self, report_period_start, report_period_end):
        domain = [('company_id', '=', self.env.company.id),
                  ('date_from', '>=', report_period_start),
                  ('date_to', '<=', report_period_end)]
        payslips = self.env['hr.payslip'].search(domain).sudo()
        return payslips
    def print_report(self):
        self.ensure_one()
        payslips_ids = self.payslip_search(
            self.report_period_start, self.report_period_end)
        if not payslips_ids:
            raise UserError(_('No payslips found for the selected period.'))
        payslips = []
        for payslip in payslips_ids:
            payslips.append(payslip.id)
        return self.env.ref('l10n_tt_hr_payroll.additions_report_action').report_action(self, data={'payslips': payslips, "report_start": self.report_period_start,
                                                                                                 "report_end": self.report_period_end, "gen_date": self.write_date, "name": self.env.user.display_name, })
class additionMonthRunReportWizard(models.TransientModel):
    _name = "deductions.report.wizard"
    _description = "Deductions Report"
    report_period_start = fields.Date("Report Period Start", required=True)
    report_period_end = fields.Date("Report Period End")
    @api.onchange("report_period_start")
    def compute_report_period_end(self):
        if (self.report_period_start != False):
            last_day = calendar.monthrange(
                self.report_period_start.year, self.report_period_start.month)[1]
            self.report_period_end = date(
                self.report_period_start.year, self.report_period_start.month, last_day)
    def payslip_search(self, report_period_start, report_period_end):
        domain = [('company_id', '=', self.env.company.id),
                  ('date_from', '>=', report_period_start),
                  ('date_to', '<=', report_period_end)]
        payslips = self.env['hr.payslip'].search(domain).sudo()
        return payslips
    def print_report(self):
        self.ensure_one()
        payslips_ids = self.payslip_search(
            self.report_period_start, self.report_period_end)
        if not payslips_ids:
            raise UserError(_('No payslips found for the selected period.'))
        payslips = []
        for payslip in payslips_ids:
            payslips.append(payslip.id)
        return self.env.ref('l10n_tt_hr_payroll.deductions_report_action').report_action(self, data={'payslips': payslips, "report_start": self.report_period_start,
                                                                                                 "report_end": self.report_period_end, "gen_date": self.write_date, "name": self.env.user.display_name, })
    class AdditionsReport(models.AbstractModel):
        _name = 'report.l10n_tt_hr_payroll.additions_report_template'
        @api.model
        def _get_report_values(self, docids, data=None):
            payslips = self.env['hr.payslip'].browse(data['payslips'])
            totals = self._get_total_totality(payslips)
            time_date = self._get_time_date(data['gen_date'])
            return {
                'doc_ids': docids,
                'doc_model': 'hr.payslip',
                'docs': payslips,
                'totals': totals,
                'date_time': time_date,
                'data': data,
            }
        def _get_total_totality(self, payslips):
            employees = 0
            additions = 0.00
            totality = self._get_additions_ytd(payslips)
            for payslip in payslips:
                for line in payslip.line_ids:
                    if line.code == "ADD":
                        additions += line.amount
                        if line.amount != 0.00:
                            employees += 1
            additions = round(additions, 2)
            return {
                "additions": additions,
                "employees": employees,
                "totality": totality,
            }
        
        def _get_additions_ytd(self, payslips):
            additions_ytd = []
            additions_type = []
            employee = []
            addition_to_employee_index = []
            addition_amount_index = []
            payslip_index = []
            
            count = 0
            sort_additions_ytd = []
            sort_employee = []
            sort_addition_to_employee_index = []
            sort_addition_amount_index = []
            sort_payslip_index = []
            for payslip in payslips:
                for addition in payslip.contract_id.salary_additions:
                    if self._is_it_present(additions_type, addition.type.name) != True:
                        additions_type.append(addition.type.name)
                    addition_to_employee_index.append(addition.type.name)
                    employee.append(payslip.contract_id.employee_id.display_name)
                    additions_ytd.append(self._employeee_additions_ytd(addition.type.name, payslip, addition))
                    addition_amount_index.append(addition.amount)
                    payslip_index.append(payslip)
            
            while(count < len(additions_type)):
                number = 0
                for item in addition_to_employee_index:
                    if(addition_to_employee_index[number] == additions_type[count]):
                        sort_additions_ytd.append(additions_ytd[number])
                        sort_employee.append(employee[number]) 
                        sort_addition_to_employee_index.append(addition_to_employee_index[number]) 
                        sort_addition_amount_index.append(addition_amount_index[number])
                        sort_payslip_index.append(payslip_index[number])
                    number += 1
                count += 1
            additions_ytd = sort_additions_ytd
            employee = sort_employee 
            addition_to_employee_index = sort_addition_to_employee_index 
            addition_amount_index = sort_addition_amount_index
            payslip_index = sort_payslip_index
            return {
                "additions_ytd": additions_ytd,
                "additions_type": additions_type,
                "employee":employee,
                "addition_to_employee":addition_to_employee_index,
                "addition_amount_index":addition_amount_index,
                "payslip":payslip_index,
            }
        
        def _is_it_present(self, list, item):
            count = 0
            while(count < len(list)):
                if list[count] == item:
                    return True
                count += 1
            return False
        
        def _employeee_additions_ytd(self, item, payslip, addition):
            additions_ytd = 0
            date_range = self._get_time_range_ytd(payslip.date_to)
            count = 0
            period_end_date = len(date_range) -1 
            while(count < (len(date_range)/2)):
                period_start_date = period_end_date - 1   
                if(addition.year_valid_to != False):
                    statement = "addition.year_valid_from <= date_range[period_start_date] and addition.year_valid_to >= date_range[period_end_date] and item == addition.type.name"
                else:
                    statement = "addition.year_valid_from <= date_range[period_start_date] and item == addition.type.name" 
                if eval(statement):
                    additions_ytd += addition.amount
                
                period_end_date -= 2
                count += 1
            return additions_ytd
        
        def _get_time_range_ytd(self, current_date):
            months_in_year = 12
            year = current_date.year
            past = []
            while (months_in_year != 0):
                max_days = calendar.monthrange(year, months_in_year)[1]
                date_obj = datetime.strptime(
                    str(year)+"-"+str(months_in_year)+"-1", '%Y-%m-%d').date()
                if(date_obj.month <= current_date.month):
                    past.append(date_obj)
                date_obj = datetime.strptime(
                    str(year)+"-"+str(months_in_year)+"-"+str(max_days), '%Y-%m-%d').date()
                
                if(date_obj.month <= current_date.month):
                    past.append(date_obj)
                months_in_year -= 1
            return past
        def _get_time_date(self, date):
            spliter = date.split()
            date_str = spliter[0]
            time_str = spliter[1]
            return {
                "time": time_str,
                "date": date_str,
            }
        
class DeductionsReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.deductions_report_template'
    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = self.env['hr.payslip'].browse(data['payslips'])
        totals = self._get_total_totality(payslips)
        time_date = self._get_time_date(data['gen_date'])
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'totals': totals,
            'date_time': time_date,
            'data': data,
        }
    def _get_total_totality(self, payslips):
            totality = self._get_deductions_ytd(payslips)
            return {
                "totality": totality,
            }
        
    def _get_deductions_ytd(self, payslips):
        deductions_ytd = []
        deductions_type = []
        employee = []
        deduction_to_employee_index = []
        deduction_amount_index = []
        payslip_index = []

        count = 0

        sort_deductions_ytd = []
        sort_employee = []
        sort_deduction_to_employee_index = []
        sort_deduction_amount_index = []
        sort_payslip_index = []
        for payslip in payslips:
            for deduction in payslip.contract_id.tax_deductions:
                if self._is_it_present(deductions_type, deduction.type.name) != True:
                    deductions_type.append(deduction.type.name)
                deduction_to_employee_index.append(deduction.type.name)
                employee.append(payslip.contract_id.employee_id.display_name)
                deductions_ytd.append(self._employeee_deductions_ytd(deduction.type.name, payslip, deduction))
                deduction_amount_index.append(self._period_deductions(payslip, deduction))
                payslip_index.append(payslip)


        while(count < len(deductions_type)):
            number = 0
            for item in deduction_to_employee_index:
                if(deduction_to_employee_index[number] == deductions_type[count]):
                    sort_deductions_ytd.append(deductions_ytd[number])
                    sort_employee.append(employee[number]) 
                    sort_deduction_to_employee_index.append(deduction_to_employee_index[number]) 
                    sort_deduction_amount_index.append(deduction_amount_index[number])
                    sort_payslip_index.append(payslip_index[number])

                number += 1

            count += 1

        deductions_ytd = sort_deductions_ytd
        employee = sort_employee 
        deduction_to_employee_index = sort_deduction_to_employee_index 
        deduction_amount_index = sort_deduction_amount_index
        payslip_index = sort_payslip_index
        return {
            "deductions_ytd": deductions_ytd,
            "deductions_type": deductions_type,
            "employee":employee,
            "deduction_to_employee":deduction_to_employee_index,
            "deduction_amount_index":deduction_amount_index,
            "payslip":payslip_index,
        }
    
    def _is_it_present(self, list, item):
        count = 0
        while(count < len(list)):
            if list[count] == item:
                return True
            count += 1

        return False

    def _period_deductions(self, payslip, deduction):

        periods = self._past_periods(payslip, deduction)

        return round(deduction.amount / periods,2)

    def _past_periods(self, payslip, deduction):
        periods = 0
        date_range = self._get_time_range_ytd(payslip.date_to)
        start_date = payslip.contract_id.date_start

        if(deduction.year_valid_to == False and payslip.date_from.year >= start_date.year and deduction.year_valid_from >= start_date):
            periods = 13 - deduction.year_valid_from.month
        elif(payslip.date_from.year >= start_date.year and deduction.year_valid_from >= start_date and deduction.year_valid_to >= payslip.date_from ):
            periods = 13 - deduction.year_valid_from.month

        return periods

    def _employeee_deductions_ytd(self, item, payslip, deduction):

        deductions_ytd = self._period_deductions(payslip, deduction)

        periods_future = self._get_remaining_periods(payslip, deduction)

        periods = self._past_periods(payslip, deduction)
        # count = 0
        # period_end_date = len(date_range) -1 

        # while(count < (len(date_range)/2)):

        #     period_start_date = period_end_date - 1   

        #     if(deduction.year_valid_to != False):
        #         statement = "deduction.year_valid_from <= date_range[period_start_date] and deduction.year_valid_to >= date_range[period_end_date] and item == deduction.type.name"
        #     else:
        #         statement = "deduction.year_valid_from <= date_range[period_start_date] and item == deduction.type.name" 

        #     if eval(statement):
        #         deductions_ytd += deduction.amount

        #     period_end_date -= 2
        #     count += 1

        # return deductions_ytd
        return deductions_ytd * (periods - periods_future)

    def _get_time_range_ytd(self, current_date):
        months_in_year = 12
        year = current_date.year
        past = []
        while (months_in_year != 0):
            max_days = calendar.monthrange(year, months_in_year)[1]
            date_obj = datetime.strptime(
                str(year)+"-"+str(months_in_year)+"-1", '%Y-%m-%d').date()
            if(date_obj.month <= current_date.month):
                past.append(date_obj)
            date_obj = datetime.strptime(
                str(year)+"-"+str(months_in_year)+"-"+str(max_days), '%Y-%m-%d').date()
            
            if(date_obj.month <= current_date.month):
                past.append(date_obj)
            months_in_year -= 1

        return past

    def _get_remaining_periods(self, payslip, deduction):
        periods = 0

        for deduction in payslip.contract_id.tax_deductions:
            if deduction.year_valid_to == False:
                periods = 13 - deduction.year_valid_from.month
                periods = periods - payslip.date_to.month
            else:
                periods = 13 + deduction.year_valid_to.month - deduction.year_valid_from.month
                periods = periods - payslip.date_to.month

        return periods

    def _get_time_date(self, date):
        spliter = date.split()
        date_str = spliter[0]
        time_str = spliter[1]
        return {
            "time": time_str,
            "date": date_str,
        }