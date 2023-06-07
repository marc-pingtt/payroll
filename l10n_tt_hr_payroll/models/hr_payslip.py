# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import calendar
from decimal import Decimal
import math
from datetime import date
from odoo.addons.hr_payroll.models.browsable_object import Payslips


class PingPayslips(Payslips):
    def sum(self, code, from_date, to_date=None):
        if to_date is None:
            to_date = fields.Date.today()
        self.env.cr.execute("""
            SELECT sum(pl.total)
            FROM hr_payslip as hp, hr_payslip_line as pl
            WHERE hp.employee_id = %s
            AND (hp.state = 'done' or hp.state = 'paid')
            AND hp.date_from >= %s
            AND hp.date_to <= %s
            AND hp.id = pl.slip_id
            AND pl.code = %s""", (self.employee_id, from_date, to_date, code))
        res = self.env.cr.fetchone()
        return res and res[0] or 0.0


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'compute_paye_salary': compute_paye_salary,
            'compute_health_surcharge': compute_health_surcharge,
            'compute_nis': compute_nis,
            'compute_additions': compute_additions,
        })
        return res

    def _get_localdict(self):
        res = super()._get_localdict()
        employee = self.employee_id
        res['employee']['age'] = compute_age(res['employee']['birthday'])
        res['payslip'] = PingPayslips(employee.id, self, self.env)
        return res


def compute_age(birthday):
    today = date.today()
    return today.year - birthday.year - \
        ((today.month, today.day) < (birthday.month, birthday.day))


def compute_nis(payslip, categories, contract):
    amount = 0.0
    contract = compute_active_contract(contract)
    total_mondays = compute_mondays_in_month(
        payslip.date_from.year, payslip.date_from.month)
    nis_rates = payslip.env['nis.rates'].search([])
    total_income = categories.GROSS
    for line in nis_rates.nis_line_ids:
        monthly_earn = line.monthly_earnings.split()
        if monthly_earn[2] != "over":
            if Decimal(monthly_earn[0]) <= total_income <= Decimal(monthly_earn[2]):
                amount = line.employees_weekly_contri
                if (contract.is_pension == True):
                    amount = 0
                cal = Decimal(amount) * total_mondays
                return Decimal(cal)
        else:
            amount = line.employees_weekly_contri
            if (contract.is_pension == True or contract.wage <= 199):
                amount = 0
            cal = Decimal(amount) * total_mondays
            return Decimal(cal)


def compute_active_contract(contracts):
    for contract in contracts:
        if contract.state == 'open':
            return contract

    print("Error No Open Contracts Available")
    return contracts  # This Only returns atm for troubleshooting purposes... but when fully deployed should not and instead kick an error message


def compute_mondays_in_month(year, month):
    return len([1 for i in calendar.monthcalendar(year, month) if i[0] != 0])


def compute_periods_remaining_nis(payslip):
    year = payslip.dict.date_from.year
    month = payslip.dict.date_from.month
    periods_remaining = compute_mondays_in_month(
        payslip.dict.date_from.year, payslip.dict.date_from.month)
    if (month != 12):
        while month < 12:
            month = month + 1
            periods_remaining += compute_mondays_in_month(year, month)
    return periods_remaining


def compute_health_surcharge(contract, payslip, categories):
    if (contract.ignore_hsur == True):
        return 0
    total_mondays = compute_mondays_in_month(
        payslip.date_from.year, payslip.date_from.month)
    basic_sal_week = (categories.BASIC * 12) / 52
    if basic_sal_week <= 109:
        health_surcharge = Decimal(
            payslip.rule_parameter('HSUR_LR')) * total_mondays
    else:
        health_surcharge = Decimal(
            payslip.rule_parameter('HSUR_UR')) * total_mondays
    return Decimal(health_surcharge)


def relevant_by_amount(contract, payslip, parameter):
    amount = 0
    if (contract.year_of_prior_validity == False):
        return amount
    if (contract.year_of_prior_validity.year == payslip.date_from.year):
        amount = eval("contract." + parameter)
    return amount


def compute_periods_remaining_month(payslip):
    end_month = 12
    start_month = payslip.date_from.month
    return end_month - start_month + 1


def _get_year_to_date_amount_for_rule(payslip, rule):
    return payslip.sum(rule, datetime(payslip.date_from.year, 1, 1), payslip.date_from)


def compute_nis_year_to_date(payslip, contract):
    nis_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'NIS')
    prior = abs(relevant_by_amount(contract, payslip, "prior_nis_paid")) * -1
    result = nis_year_to_date + prior
    return result


def compute_projected_nis_deductions(payslip, nis):
    remaining_periods_nis = compute_periods_remaining_nis(payslip)
    weekly_deductible_nis = (nis /
                             compute_mondays_in_month(
                                 payslip.dict.date_from.year, payslip.dict.date_from.month) * payslip.rule_parameter('NIS_%'))
    return remaining_periods_nis * weekly_deductible_nis


def compute_valid_credits_or_deductions_for(payslip, contract, item_name, tax_field):
    amount = 0
    aggregator = eval("contract." + tax_field)
    items = [item for item in aggregator if is_valid_cred_and_deduct(
        item_name, payslip, aggregator)]
    for item in items:
        amount += item.amount
    return abs(amount)


def is_valid_cred_and_deduct(cred_duc_name, payslip, extras):
    for extra in extras:
        if (extra.year_valid_to != False):
            if (extra.type.name == cred_duc_name and (extra.year_valid_from < payslip.date_to or extra.year_valid_to >= payslip.date_to)):
                return True
            if (extra.type.name == cred_duc_name and extra.year_valid_from < payslip.date_to):
                return True
        if (extra.type.name == cred_duc_name and extra.year_valid_from.year >= payslip.date_from.year):
            if (payslip.date_from.month >= extra.year_valid_from.month):
                return True
        # Place Holder Function just to get National Tax Savings Bond working, will refactor to make nicer.
        NTSB = "NATIONAL TAX SAVINGS BONDS MATURITY YEAR "
        if (cred_duc_name == (NTSB + '5') or cred_duc_name == (NTSB + '7') or cred_duc_name == (NTSB + '10')):
            if (payslip.date_from.year == extra.year_valid_from.year + 5 or payslip.date_from.year == extra.year_valid_from.year + 7 or payslip.date_from.year == extra.year_valid_from.year + 10):
                return True
    return False


def compute_additions(payslip, contract, param):
    contract = compute_active_contract(contract)
    amount = 0

    def is_valid_today(parameter, payslip):
        if (parameter.year_valid_to != False):
            if (parameter.year_valid_from <= payslip.date_from and parameter.year_valid_to >= payslip.date_to):
                return True
        if (parameter.year_valid_from <= payslip.date_from and parameter.year_valid_to == False):
            return True
        if (parameter.year_valid_to.month == payslip.date_to.month and parameter.year_valid_to.year == payslip.date_to.year):
            return True
        return False

    parameters = [parameter for parameter in eval("contract."+param) if is_valid_today(
        parameter, payslip)]
    for parameter in parameters:
        amount += parameter.amount
    return amount


def compute_greater_than_for(amount, limit):
    if (amount > limit):
        return limit
    return amount


def compute_greater_than_for_with_percentile_range(amount, payslip, rule_prefix):
    if (amount/100*payslip.rule_parameter(rule_prefix + '_%') > payslip.rule_parameter(rule_prefix + '_V')):
        return payslip.rule_parameter(rule_prefix + '_V')
    return amount


def compute_tertiary_deductions(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "TERTIARY EDUCATION EXPENSES", "tax_deductions")
    limit = payslip.rule_parameter('TEDEXP')
    return compute_greater_than_for(amount, limit)


def compute_first_time_home_owner(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "FIRST TIME HOME OWNER", "tax_deductions")
    limit = payslip.rule_parameter('FTHO')
    return compute_greater_than_for(amount, limit)


def compute_deed_of_covenant(payslip, contract, chargeable_income):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "DEED OF COVENANT", "tax_deductions")
    limit = chargeable_income/100*payslip.rule_parameter('DOCOV')
    return compute_greater_than_for(amount, limit)


def compute_contributions(payslip, contract, nis_projected_deductions):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "CONTRIBUTIONS/PREMIUMS PAID", "tax_deductions") + abs(nis_projected_deductions)
    limit = payslip.rule_parameter('CONTRIB')
    return compute_greater_than_for(amount, limit)


def compute_alimony_or_maintainance(payslip, contract):
    return compute_valid_credits_or_deductions_for(payslip, contract, "ALIMONY / MAINTAINANCE", "tax_deductions")


def compute_travelling_expenses(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "TRAVELLING EXPENSES", "tax_deductions")
    return amount/100*payslip.rule_parameter('TRAV_EXP')


def compute_solar_water_heater(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "SOLAR WATER HEATER", "tax_credits")
    return compute_greater_than_for_with_percentile_range(amount, payslip, "SWH")


def compute_cng_cylinders(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "CNG KIT AND CYLINDER", "tax_credits")
    return compute_greater_than_for_with_percentile_range(amount, payslip, "CNG")


def compute_guesthouse_conversion(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "GUEST HOUSE CONVERSION", "tax_deductions")
    return amount


def compute_venture_tax_credit(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "VENTURE CAPITAL INVESTMENT", "tax_credits")
    if (amount != 0):
        return amount*payslip.rule_parameter("VCITC_%")
    return amount


def compute_national_tax_free_savings_bond(payslip, contract):
    amount = 0
    array_year = [payslip.rule_parameter('NTFSB_5'), payslip.rule_parameter(
        'NTFSB_7'), payslip.rule_parameter('NTFSB_10')]
    year = 0
    while year <= array_year[2]:
        if ([credit for credit in contract.tax_credits if credit.type.name == "NATIONAL TAX SAVINGS BONDS MATURITY YEAR " + str(year) and (credit.year_valid_from.year + payslip.rule_parameter('NTFSB_' + str(year))) == payslip.date_to.year]):
            amount += compute_valid_credits_or_deductions_for(
                payslip, contract, "NATIONAL TAX SAVINGS BONDS MATURITY YEAR " + str(year), "tax_credits")
        year += 1
    return compute_greater_than_for_with_percentile_range(amount, payslip, "NTFSB")


def compute_annual_tax_credits(payslip, contract):
    annual_credits = 0
    annual_credits += compute_venture_tax_credit(payslip, contract)
    annual_credits += compute_national_tax_free_savings_bond(payslip, contract)
    annual_credits += compute_solar_water_heater(payslip, contract)
    annual_credits += compute_cng_cylinders(payslip, contract)
    return round(annual_credits, 2)


def compute_annual_deductions(payslip, annual_income, contract, nis_this_month):
    total_nis_tax_allowance_so_far = compute_nis_year_to_date(
        payslip, contract)
    annual_deductions = payslip.rule_parameter('PALLOW')
    nis_projected_deductions = round(
        compute_projected_nis_deductions(payslip, nis_this_month), 2)
    annual_deductions += compute_tertiary_deductions(payslip, contract)
    annual_deductions += compute_first_time_home_owner(payslip, contract)
    annual_deductions += compute_deed_of_covenant(
        payslip, contract, annual_income)
    annual_deductions += compute_contributions(
        payslip, contract, nis_projected_deductions)
    # Refector to use rule parameter
    annual_deductions += abs(total_nis_tax_allowance_so_far) * 0.7
    annual_deductions += compute_alimony_or_maintainance(payslip, contract)
    annual_deductions += compute_travelling_expenses(payslip, contract)
    annual_deductions += compute_guesthouse_conversion(payslip, contract)
    annual_deductions = round(annual_deductions, 2)
    return annual_deductions


def compute_annual_paye(annual_income, chargeable_income, payslip, annual_tax_credits):
    rate = Decimal(payslip.rule_parameter('PAYE_LB'))
    if annual_income > Decimal(payslip.rule_parameter('PAYE_T')):
        rate = Decimal(payslip.rule_parameter('PAYE_UB'))
    annual_paye = (Decimal(chargeable_income) * rate) - \
        Decimal(annual_tax_credits)
    if (annual_paye < 0):
        annual_paye = 0
    return annual_paye


def compute_paye_salary(payslip, categories, contract):
    gross_salary = categories.GROSS
    other_income = sum(contract.get_valid_other_income_sources(
        payslip.date_to).mapped('amount'))
    gross_income = gross_salary + other_income
    periods_remaining = compute_periods_remaining_month(payslip)
    projected_salary = gross_salary * periods_remaining
    projected_income = gross_income * periods_remaining
    if payslip.date_to.month == 1:
        salary_year_to_date = 0
        income_year_to_date = 0
    else:
        salary_year_to_date = payslip.sum('GROSS', datetime(
            payslip.date_to.year, 1, 1), payslip.date_to) + relevant_by_amount(contract, payslip, "prior_earnings")
        # Test setting a date prior to the start of the payslip year
        other_income_sources_year_to_date = [contract.get_valid_other_income_sources(date(
            payslip.date_from.year, x, 1)).mapped('amount') for x in range(1, payslip.date_from.month)]
        income_year_to_date = salary_year_to_date + \
            sum([sum(x) for x in other_income_sources_year_to_date])
    annual_salary = projected_salary + salary_year_to_date
    annual_income = projected_income + income_year_to_date
    annual_deductions = compute_annual_deductions(
        payslip, annual_income, contract, categories.NIS)
    chargable_income = annual_income - annual_deductions
    if annual_salary < chargable_income:
        annual_paye = compute_annual_paye(
            annual_income, annual_salary, payslip, compute_annual_tax_credits(payslip, contract))
    else:
        annual_paye = compute_annual_paye(
            chargable_income, chargable_income, payslip, compute_annual_tax_credits(payslip, contract))
    paye_year_to_date = payslip.sum('PAYE', datetime(
        payslip.date_to.year, 1, 1), payslip.date_to) - abs(relevant_by_amount(contract, payslip, "prior_paye_paid"))
    remaining_paye = annual_paye - Decimal(abs(paye_year_to_date))
    monthly_paye = remaining_paye / periods_remaining
    return Decimal(monthly_paye)
