from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from decimal import Decimal
import math

class td4ReportWizard(models.TransientModel):
    _name = 'td4.report.wizard'
    _description = 'TD4 Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    year = fields.Selection([(str(y), str(y)) for y in range(1990, datetime.now().year+1)], 'Year', required=True)

    def has_payslip(self, employee_id):
        """This fuction is used to tell if the employee has a payslip"""
        return True if self.env['hr.payslip'].search([('employee_id', '=', employee_id)]) else False

    def _get_report_base_filename(self, employee):
        """This function is used to get the report file name"""

        employee.ensure_one()
        return 'TD4 Report-%s' % (employee.name)
        
    def get_td1_total_deductions_for(self, employee, year):                                                   
        """The function returns the total deductions as per TD1"""
        aggregator = 0.0
        personal_allowance = self.rule_parameter('PALLOW', date(int(year), 1, 1))

        nis = self.get_nis_deduction_for(employee, year)
        aggregator = (Decimal(nis) + Decimal(personal_allowance))
        #if aggregator >= put contrib and nis rule max here

        return aggregator

    def get_td1_remuneration_before_deductions_for(self, employee, year):
        #TODO: Complete implementation or something, Johsua will know what to do.. faith is apprecitaed but idk
        payslips = self.lambda_done_search(employee, year)
        
        renumerations = self.get_gross_earnings_for(employee, year)

        return renumerations

    def lambda_done_search(self, employee, year):

        return employee.slip_ids.filtered(
            lambda x: x.state == 'done' and x.date_from.year == int(year))

    def get_total_weeks_employed_for(self, employee, year):

        earliest_date = date.today()

        payslips = self.lambda_done_search(employee, year)
        
        for payslip in payslips:
            if earliest_date > payslip.date_from:
                earliest_date = payslip.date_from

        payslips = employee.slip_ids.filtered(
            lambda x: x.state != 'cancel' and x.date_from.year == int(year))

        latest_date = earliest_date

        for payslip in payslips:
            if latest_date < payslip.date_to:
                latest_date = payslip.date_to

        date_delta = latest_date - earliest_date
        week_delta = date_delta.days
        week_delta = math.ceil(week_delta/7)

        return week_delta

    def get_commisions_for(self, employee, year):
        #TODO: w/e this is , Is this for people who work by commision or wages complimented by tipping?
        return 0

    def get_taxable_allowance_for(self, employee, year):
        payslips = self.lambda_done_search(employee, year)
        
        allowances = 0.0
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == 'ADD':
                    allowances += line.amount
        return allowances

    def get_travel_allowance_for(self, employee, year):
        #If Needed It follows the same format as every other taxable allowance
        payslips = self.lambda_done_search(employee, year)  
        allowances = 0.0
        return allowances

    def get_other_allowances_for(self, employee, year):
        payslips = self.lambda_done_search(employee, year)
        allowances = 0.0
        return allowances

    def get_gross_earnings_for(self, employee, year):
        payslips = self.lambda_done_search(employee, year)

        gross = 0.0
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == 'GROSS':
                    gross += line.amount

        return gross

    def get_nis_deduction_for(self, employee, year):
        payslips = self.lambda_done_search(employee, year)

        nis = 0.0
        for payslip in payslips:
            #TODO: Optimize all payslip loops
            for line in payslip.line_ids:
                if line.code == 'NIS':
                    nis += line.amount

        deductible_percent = self.rule_parameter('NIS_%', date(int(year), 1, 1))

        return (abs(Decimal(nis))*(Decimal(deductible_percent)))

    def get_paye_so_for(self, employee, year):
        payslips = self.lambda_done_search(employee, year)

        paye = 0.0
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == 'PAYE':
                    paye += line.amount

        return paye

    def get_health_surcharge_deducted_for(self, employee, year):
        payslips = self.lambda_done_search(employee, year)

        total_hsur = 0.0
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == 'HSUR':
                    total_hsur += line.amount

        return total_hsur


    def get_hsur_rate_finder(self, employee, year, switch):
        payslips = self.lambda_done_search(employee, year)

        week_counter = 0

        salary = employee.contract_ids.wage
        sal_type = employee.contract_ids.wage_type
        sal_type = sal_type.upper()

        salary_emol = self.rule_parameter('HSUR_'+sal_type, date(int(year), 1, 1))

        if Decimal(salary_emol) <= salary and switch != 'LR':
            switch = 1
        elif switch == "LR" and Decimal(salary_emol) >= salary :
            switch = 1

        if switch == 1:
            for payslip in payslips:
                for worked_days in payslip.worked_days_line_ids:
                    attendance = worked_days.number_of_days
                    for line in payslip.line_ids:
                        if line.code == 'HSUR':
                            week_counter += (attendance / 5)

        return round(week_counter,0)

    def get_address_from(self, contact):

        address = ''
        if contact.street is not None and contact.street is not False:
            address = contact.street+"\n"
        if contact.street2 is not None and contact.street2 is not False:
            address = address + contact.street2+"\n"
        if contact.city is not None and contact.city is not False:
            address = address + contact.city+"\n"
        if contact.state_id.name is not None and contact.state_id.name is not False:
            address = address + contact.state_id.name+"\n"
        if contact.country_id.display_name is not None and contact.country_id.display_name is not False:
            address = address + contact.country_id.display_name

        return address

    

    def preview_report(self):
        year_select = int(self.year)
        next_year_date = datetime(year_select + 1, 1, 1)
        last_day = next_year_date - timedelta(days=4)
        total_weeks = last_day.isocalendar()[1]
        data = {'year': self.year, 'total_weeks': total_weeks}
        lst = []

        if self.employee_ids:
            for employee in self.employee_ids:  
                if self.has_payslip(employee.id):
                    name = self._get_report_base_filename(employee)
                    obj = self.env['td4.edit'].create(
                        {
                            'year': self.year,
                            'name': name,
                            'employee_name': employee.name,
                            'employee_address': self.get_address_from(employee.address_home_id),
                            'employer_name': employee.company_id.partner_id.name,
                            'employer_address': self.get_address_from(employee.company_id),
                            'employee_bir_number': employee.bir_file_number,
                            'employee_nis_number': employee.nis_number,
                            'employer_paye_number': employee.company_id.paye_file_number,
                            'employer_bir_number': employee.company_id.bir_file_number,
                            'total_deductions': self.get_td1_total_deductions_for(employee, self.year),
                            'week_employed': self.get_total_weeks_employed_for(employee, self.year),
                            'remuneration_before': self.get_td1_remuneration_before_deductions_for(employee, self.year),
                            'commissions': self.get_commisions_for(employee, self.year),
                            'taxable_allowance': self.get_taxable_allowance_for(employee, self.year),
                            'travel_allowance': self.get_travel_allowance_for(employee, self.year),
                            'other_allowance': self.get_other_allowances_for(employee, self.year),
                            'income_relate_previous': '',
                            'saving_plan': '',
                            'gross_earnings': self.get_gross_earnings_for(employee, self.year),
                            'employer_contribution': '',
                            'travel_dispensation': '',
                            'employee_contribution': '',
                            'nis_deduction': self.get_nis_deduction_for(employee, self.year),
                            'paye_deduction': self.get_paye_so_for(employee, self.year),
                            'no_of_weeks_health': self.get_hsur_rate_finder(employee, self.year, 1),
                            'no_of_weeks_at_8_25': self.get_hsur_rate_finder(employee, self.year, 'UR'),
                            'no_of_weeks_at_4_80': self.get_hsur_rate_finder(employee, self.year, 'LR'),
                            'health_deductions': self.get_health_surcharge_deducted_for(employee, self.year),
                        })
                    lst.append(obj.id)
        else: 
            employees = self.env['hr.employee'].search([])    
            for employee in employees:
                payslip = self.env['hr.payslip'].search([('employee_id', '=', employee.id)])
                if payslip:
                    obj = self.env['td4.edit'].create(
                        {
                            'year': self.year,
                            'name': name,
                            'employee_name': employee.name,
                            'employee_address': self.get_address_from(employee.address_home_id),
                            'employer_name': employee.company_id.partner_id.name,
                            'employer_address': self.get_address_from(employee.company_id),
                            'employee_bir_number': employee.bir_file_number,
                            'employee_nis_number': employee.nis_number,
                            'employer_paye_number': employee.company_id.paye_file_number,
                            'employer_bir_number': employee.company_id.bir_file_number,
                            'total_deductions': self.get_td1_total_deductions_for(employee, self.year),
                            'week_employed': self.get_total_weeks_employed_for(employee, self.year),
                            'remuneration_before': self.get_td1_remuneration_before_deductions_for(employee, self.year),
                            'commissions': self.get_commisions_for(employee, self.year),
                            'taxable_allowance': self.get_taxable_allowance_for(employee, self.year),
                            'travel_allowance': self.get_travel_allowance_for(employee, self.year),
                            'other_allowance': self.get_other_allowances_for(employee, self.year),
                            'income_relate_previous': '',
                            'saving_plan': '',
                            'gross_earnings': self.get_gross_earnings_for(employee, self.year),
                            'employer_contribution': '',
                            'travel_dispensation': '',
                            'employee_contribution': '',
                            'nis_deduction': self.get_nis_deduction_for(employee, self.year),
                            'paye_deduction': self.get_paye_so_for(employee, self.year),
                            'no_of_weeks_health': self.get_hsur_rate_finder(employee, self.year, 1),
                            'no_of_weeks_at_8_25': self.get_hsur_rate_finder(employee, self.year, 'UR'),
                            'no_of_weeks_at_4_80': self.get_hsur_rate_finder(employee, self.year, 'LR'),
                            'health_deductions': self.get_health_surcharge_deducted_for(employee, self.year),
                        })
                    lst.append(obj.id)

        return {
            'name': "TD4 Report",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'td4.edit',
            'domain': [('id', 'in', lst)],
            'target': 'current'

        }

    def report_summary(self):

        data = {'year': self.year, 'employee_ids': self.employee_ids.ids}
        return self.env.ref('l10n_tt_hr_payroll.employee_summary_report').report_action(self.employee_ids, data=data)

    def rule_parameter(self, code, date):
        return self.env['hr.rule.parameter']._get_parameter_from_code(code, date)