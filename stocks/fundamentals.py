import argparse
import json
import logging
import os
import urllib.request
import requests
import numpy as np
from tabulate import tabulate
from utils.millify import millify
from utils.translate import Translator
import utils.scrappers.investing as inv
import utils.scrappers.yahoo_finance as yf


logging.basicConfig(level=logging.INFO, format=f"%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Perform a fundamental analysis of a compagny")
parser.add_argument("symbol", type=str, help="The company's symbol")
parser.add_argument("-k", "--apikey", type=str, help="Yahoo Finance API key")
parser.add_argument("-u", "--update", action="store_true", default=False, help="Update cached company data")
parser.add_argument("-l", "--language", default="en", help="Language")

args = parser.parse_args()

# get translator
tr = Translator(args.language)

# fetch api key(s)
keys = []
if args.apikey:
    keys.append(args.apikey)
else:
    keys = yf.get_api_keys()
    if not keys:
        print(tr("No keys found, please provide an API key or create an empty file and name it with the API key and place you key in key(s) under <keys> directory"))
        exit(0)

# update cache
update = args.update

# convert company symbol to uppercase
symbol = args.symbol.upper()

# create cache directory if it doesn't exit
cache_dir = "./cache"
if not os.path.exists(cache_dir):
    logger.debug("Creating cache folder")
    os.mkdir(cache_dir)

filename = os.path.join(cache_dir, symbol + ".json")
if not os.path.exists(filename):
    update = True

data = []
if update:
    # fetch company's data
    print(tr('Downloading the company\'s data...'))
    # fetch company's financials
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-financials"
    querystring = {"symbol": symbol}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': keys[0]
    }
    response = requests.request("GET", url, headers=headers, params=querystring,)
    if not response:
        print(tr('The company\'s financial data could not be downloaded for the following reason') +': ', response.reason)
    else:
        data.append(response.json())
    # fetch company's balance-sheet
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-balance-sheet"
    response = requests.request("GET", url, headers=headers, params=querystring,)
    if not response:
        print(tr('The company\'s balance-sheet data could not be downloaded for the following reason') +': ', response.reason)
    else:
        data.append(response.json())
    if data:
        print(tr('Successfuly downloaded the company\'s data'))
        # store company's data as json
        outfile = open(filename, 'w')
        json.dump(data, outfile, indent=4)
else:
    print(tr('Loading cached company\'s data...'))
    infile = open(filename)
    data = json.load(infile)
    print(tr('Successfuly loaded cached company\'s data'))

print('\n')

equity = inv.Equity(symbol)

### exctract infos
financials = data[0]
company_name = financials['quoteType']['longName']
if len(financials['summaryDetail']['marketCap']) > 0:
    market_cap = financials['summaryDetail']['marketCap']['raw']
else:
    market_cap = equity.balance_sheet().total_common_shares_outstanding()[0] * financials['price']['regularMarketOpen']['raw']

## income statement
income_statements = financials['incomeStatementHistory']['incomeStatementHistory']
if 'totalRevenue' in income_statements[0]:
    revenue = income_statements[0]['totalRevenue']['raw']
else:
    revenue = None
    logger.warning("Revenue value could not be found")

ebit = income_statements[0]['ebit']['raw']
earnings = income_statements[0]['netIncome']['raw']
net_income_applicable_to_common_shares = income_statements[0]['netIncomeApplicableToCommonShares']['raw']
gross_profit = income_statements[0]['grossProfit']['raw']
operating_income = income_statements[0]['operatingIncome']['raw']
net_income = income_statements[0]['netIncome']['raw']

common_shares_outstaning = equity.balance_sheet().total_common_shares_outstanding()[0]

# interest expense
if len(income_statements[0]['interestExpense']) > 0:
    interest_expense = income_statements[0]['interestExpense']['raw']
elif len(financials['timeSeries']['annualInterestExpense']) > 0:
    annual_interest_expense = financials['timeSeries']['annualInterestExpense']
    if annual_interest_expense[-1]:
        interest_expense = annual_interest_expense[-1]['reportedValue']['raw']
    else:
        interest_expense = None
        logger.warning("Interest expense value could not be found")
else:
    interest_expense = None
    logger.warning("Interest expense value could not be found")

if len(income_statements[0]['sellingGeneralAdministrative']) > 0:
    sga = income_statements[0]['sellingGeneralAdministrative']['raw']
else:
    sga = None
    logger.warning("SG&A value could not be found")

operating_expense = income_statements[0]['totalOperatingExpenses']['raw']

annual_ebitda = financials['timeSeries']['annualEbitda']
if len(annual_ebitda) > 0:
    ebitda = annual_ebitda[-1]['reportedValue']['raw']
else:
    ebitda = None
    logger.warning("EBITDA value could not be found")

## balance-sheet
balance_sheet = data[1]
balance_sheet_statements = balance_sheet['balanceSheetHistory']['balanceSheetStatements']
total_assets = balance_sheet_statements[0]['totalAssets']['raw']
stockholder_equity =  balance_sheet_statements[0]['totalStockholderEquity']['raw']

if 'propertyPlantEquipment' in balance_sheet_statements[0]:
    property_plant_equipment = balance_sheet_statements[0]['propertyPlantEquipment']['raw']
else:
    property_plant_equipment = None
    logger.warning("Property Plant Equipment value could not be found")

# intangible_assets = balance_sheet_statements[0]['intangibleAssets']['raw']
current_assets = balance_sheet_statements[0]['totalCurrentAssets']['raw']
current_liabilities = balance_sheet_statements[0]['totalCurrentLiabilities']['raw']

annual_long_term_debt = balance_sheet['timeSeries']['annualLongTermDebt']
if len(annual_long_term_debt) > 0 and annual_long_term_debt[-1]:
    long_term_debt = annual_long_term_debt[-1]['reportedValue']['raw']
else:
    if 'longTermDebt' in balance_sheet_statements[0]:
        long_term_debt = balance_sheet_statements[0]['longTermDebt']['raw']
    else:
        long_term_debt = None
        logger.warning("Annual long term debt value could not be found")

annual_cash_and_cash_equivalents = balance_sheet['timeSeries']['annualCashAndCashEquivalents']
if len(annual_cash_and_cash_equivalents) > 0 and annual_cash_and_cash_equivalents[-1]:
    cash_and_cash_equivalents = annual_cash_and_cash_equivalents[-1]['reportedValue']['raw']
else:
    cash_and_cash_equivalents = None
    logger.warning("Cash and cash equivalents value could not be found")

annual_other_short_term_investments = balance_sheet['timeSeries']['annualOtherShortTermInvestments']
if len(annual_other_short_term_investments) > 0 and annual_other_short_term_investments[-1]:
    other_short_term_investments = annual_other_short_term_investments[-1]['reportedValue']['raw']
else:
    other_short_term_investments = None
    logger.warning("Other short term investments value could not be found")

annual_accounts_receivable = balance_sheet['timeSeries']['annualAccountsReceivable']
if len(annual_accounts_receivable) > 0 and annual_accounts_receivable[-1]:
    accounts_receivable = annual_accounts_receivable[-1]['reportedValue']['raw']
else:
    accounts_receivable = None
    logger.warning("Accounts receivable value could not be found")

# goodwill = balance_sheet['timeSeries']['annualGoodwill'][-1]['reportedValue']['raw']

annual_current_debt = balance_sheet['timeSeries']['annualCurrentDebt']
if len(annual_current_debt) > 0 and annual_current_debt[-1]:
    short_term_debt = annual_current_debt[-1]['reportedValue']['raw']
else:

    # gives only an approximation
    short_term_debt = equity.balance_sheet().current_debt_and_capital_lease_obligation()[0]
    logger.warning("Short term debt value may not be very accurate")

## cash flow
cash_flow = financials['cashflowStatementHistory']['cashflowStatements']

if 'capitalExpenditures' in cash_flow[0]:
    capital_expenditures = cash_flow[0]['capitalExpenditures']['raw']
elif 'capitalExpenditures' in cash_flow[1]:
    capital_expenditures = cash_flow[1]['capitalExpenditures']['raw']
else:
    capital_expenditures = None
    logger.warning("Capital expenditures value could not be found")

if 'depreciation' in cash_flow[0]:
    depreciation = cash_flow[0]['depreciation']['raw']
elif 'depreciation' in cash_flow[1]:
    depreciation = cash_flow[1]['depreciation']['raw']
else:
    depreciation = None
    logger.warning("Depreciation value could not be found")

buffet_approved = 0
buffet_criterias = 0
buffet_approved_summary = ''
buffet_not_approved_summary = ''

slater_approved = 0
slater_criterias = 0
slater_approved_summary = ''
slater_not_approved_summary = ''

mayer_approved = 0
mayer_criterias = 0
mayer_approved_summary = ''
mayer_not_approved_summary = ''

print('\n' + tr('Fundamental analysis of') + ' {} :\n'.format(company_name))

# predict next year earnings using linear regression
l = len(income_statements)
print(income_statements)
n = int(np.floor(np.divide(l, 3)))
m = len(income_statements) - (n * 2)

y1 = 0
e1 = 0
for i in reversed(range(0, n)):
    y1 += int(income_statements[i]['endDate']['fmt'][:4])
    e1 += income_statements[i]['netIncome']['raw']
y1 /= n
e1 /= n
m1 = (y1, e1)

y2 = 0
e2 = 0
for i in reversed(range(n, l - n)):
    y2 += int(income_statements[i]['endDate']['fmt'][:4])
    e2 += income_statements[i]['netIncome']['raw']
y2 /= l - (n * 2)
e2 /= l - (n * 2)
m2 = (y2, e2)

y3 = 0
e3 = 0

for i in reversed(range(l-n, l)):
    y3 += int(income_statements[i]['endDate']['fmt'][:4])
    e3 += income_statements[i]['netIncome']['raw']
y3 /= n
e3 /= n
m3 = (y3, e3)

p = ((m1[0]+m2[0]+m3[0]) / 3, (m1[1]+m2[1]+m3[1]) / 3)

a = (m3[1]-m1[1])/(m3[0]-m1[0])
b = p[1] - (a * p[0])

earnings_table_headers = []
earnings_table = []
for i in reversed(range(l)):
        earnings_table_headers.append(income_statements[i]['endDate']['fmt'][:4])
        earnings_table.append(income_statements[i]['netIncome']['fmt'])

earnings_table_headers.append('Est. {}'.format(int(income_statements[0]['endDate']['fmt'][:4]) + 1))
earnings_table.append(millify(a * (int(income_statements[0]['endDate']['fmt'][:4]) + 1) + b))
print('\n* ' + tr('Change in net income') + ':\n\n+' + tabulate([earnings_table], headers=earnings_table_headers) + '\n')

## market cap
if market_cap:
    slater_criterias += 1
    if market_cap > 300e6 and market_cap < 2e9:
        slater_approved += 1
        slater_approved_summary += '\n-' + tr('Slater likes smallcaps')
    else:
        slater_not_approved_summary += '\n-' + tr('Slater prefers smallcaps')

    mayer_criterias += 1
    price_to_sales_ratio = equity.ratios().price_to_sales_ttm()
    if (market_cap > 300e6 and market_cap < 700e6) and (revenue > 140e6 and revenue < 200e6) \
        and (price_to_sales_ratio > 2.5 and price_to_sales_ratio < 3.5):
        mayer_approved += 1
        mayer_approved_summary += "\n-" + tr("Mayer may consider this company as a potential 100-bagger provided it has and international expansion potential")
    else:
        mayer_not_approved_summary += "\n-" + tr("Mayer may not consider this company as a potential 100-bagger")

## profitability
print(tr('Profitability') + ':')

# gross margin
gross_margin = gross_profit / revenue * 100
buffet_criterias += 1
if gross_margin > 40:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + tr('The gross margin is higher than') + ' 40% ({:.2f}%)'.format(gross_margin)
else:
    buffet_not_approved_summary += '\n-' + tr('The gross margin is lower than') + ' 40% ({:.2f}%)'.format(gross_margin)
print(tr('Gross margin') + ' (TTM): {:.2f}%'.format(gross_margin))

# operating margin
operating_margin = operating_income / revenue * 100
print(tr('Operating margin') + ' (TTM): {:.2f}%'.format(operating_margin))

# net margin
net_margin = net_income / revenue * 100
buffet_criterias += 1
if net_margin > 20:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + tr('The net margin is higher than') + ' 20% ({:.2f}%)'.format(net_margin)
else:
    buffet_not_approved_summary += '\n-' + tr('The net margin is lower than') + ' 20% ({:.2f}%)'.format(net_margin)
print(tr('Net margin') + ' (TTM): {:.2f}%'.format(net_margin))

## overall financial performance
print('\n' + tr('Overral financial performance') + ':')

if short_term_debt and long_term_debt and market_cap:
    # ev / ebitda ratio
    if cash_and_cash_equivalents and ebitda:
        total_debt =  short_term_debt + long_term_debt
        enterprise_value = market_cap + total_debt - cash_and_cash_equivalents
        ev_ebitda_ratio = enterprise_value / ebitda
        comment = tr('bad')
        if ev_ebitda_ratio < 11:
            comment = tr('excellent')
        elif ev_ebitda_ratio < 14:
            comment = tr('good')
        print('EV/EBITDA: {:.2f} -> {}'.format(enterprise_value / ebitda, comment))

    # ebit / ev multiple
    ebit_ev_multiple = ebit / enterprise_value
    print('EBIT/EV: {:.2f}x'.format(ebit_ev_multiple))

# eps
if net_income_applicable_to_common_shares:
    basic_eps = net_income_applicable_to_common_shares / common_shares_outstaning
else:
    basic_eps = net_income / common_shares_outstaning

# pe ratio
per = (market_cap / common_shares_outstaning) / basic_eps
comment = tr("bad")
if per <= 10:
    comment = tr("excellent")
elif per <= 12:
    comment = tr("bon")
print("P/E Ratio: {:.2f} -> {}".format(per, comment))

## management effectivness
print('\n' + tr('Management effectivness') + ':')
# roa
roa = net_income / total_assets * 100
comment = tr('bad')
if roa > 5:
    comment = tr('good')
if roa > 10:
    comment = tr('excellent')
print('ROA (TTM): {:.2f}% -> {}'.format(roa, comment))

# roce (return on capital employed)
slater_criterias += 1
capital_employed = total_assets - current_liabilities
roce = ebit / capital_employed * 100
comment = '...'
if roce > 20:
    comment = tr('excellent')
    slater_approved += 1
    slater_approved_summary += '\n-' + tr('The return on capital employed is higher than') + ' 20% ({:.2f}%)'.format(roce)
else:
    slater_not_approved_summary += '\n-' + tr('The return on capital employed is lower than') + ' 20% ({:.2f}%)'.format(roce)
print('ROCE (TTM): {:.2f}% -> {}'.format(roce, comment))

# roe
roe = net_income / stockholder_equity * 100
comment = tr('bad')
if roe >= 15 and roe <= 20:
    comment = tr('good')
elif roe > 20:
    comment = tr('excellent')
print('ROE (TTM): {:.2f}% -> {}'.format(roe, comment))

## balance sheet
print('\n' + tr('Balance sheet') + ':')

# current ratio
buffet_criterias += 1
current_ratio = current_assets / current_liabilities
if current_ratio > 1.5:
    comment = tr('good')
    buffet_approved += 1
    buffet_approved_summary += '\n-' + tr('The current ratio is higher than') + ' 1.5 ({:.2f})'.format(current_ratio)
    if (current_ratio > 2.5):
        buffet_approved_summary += '\n-' + tr('However, you should note that the current ratio is higher than') + ' 2.5, ' + tr('which may indicate mismanagement of money due to an inability to collect payments')
else:
    comment = tr('bad')
    buffet_not_approved_summary += '\n-' + tr('The current ratio is lower than') + ' 1.5 ({:.2f})'.format(current_ratio)
    if current_ratio < 1:
        comment = tr('very bad')
        buffet_not_approved_summary += '\n-' + tr('The company must acquire new debt to pay its debt obligations')
print(tr('Current ratio') + ' (TTM): {:.2f} -> {}'.format(current_ratio, comment))

# quick ratio
if other_short_term_investments and accounts_receivable and cash_and_cash_equivalents:
    slater_criterias += 1
    quick_ratio = (cash_and_cash_equivalents + other_short_term_investments + accounts_receivable) / current_liabilities
    if quick_ratio > 1:
        slater_approved += 1
        slater_approved_summary += '\n-' + tr('The company has good financials, it\'s QR is higher than') + ' 1 ({:.2f})'.format(quick_ratio)
        if quick_ratio <= 1.5:
            comment = tr('good')
        elif quick_ratio > 1.5:
            comment = tr('excellent')
    else: 
        comment = tr('bad')
        slater_not_approved_summary += '\n-' + tr('The company doesn\'t have good financials, it\'s QR is lower than') + ' 1 ({:.2f})'.format(quick_ratio)
    print('QR (TTM): {:.2f} -> {}'.format(quick_ratio, comment))

if sga:
    buffet_criterias += 1
    sga_to_gross_margin_ratio = sga * 100 / gross_profit
    if sga_to_gross_margin_ratio < 30:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('Selling, General and Administrative expenses represent less than 30% of the gross margin') + ' ({:.2f}%)'.format(sga_to_gross_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + tr('Selling, General and Administrative expenses represent more than 30% of the gross margin') + ' ({:.2f}%)'.format(sga_to_gross_margin_ratio)
# else:
#     operating_expense_to_gross_margin_ratio = operating_expense * 100 / gross_profit
#     if operating_expense_to_gross_margin_ratio < 70:
#         buffet_approved += 1
#         buffet_approved_summary += '\n-Les frais d\'exploitation représentent moins de 70% de la marge brute ({:.2f}%)'.format(operating_expense_to_gross_margin_ratio)
#     else:
#         buffet_not_approved_summary += '\n-Les frais d\'exploitation représentent plus de 70% de la marge brute ({:.2f}%)'.format(operating_expense_to_gross_margin_ratio)

# depretiation to gross margin
if depreciation:
    buffet_criterias += 1
    depreciation_to_gross_margin_ratio = depreciation * 100 / gross_profit
    if depreciation_to_gross_margin_ratio < 15:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('The depreciation is low') + ' ({:.2f}%)'.format(depreciation_to_gross_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + tr('The depreciation is high') + ' ({:.2f}%)'.format(depreciation_to_gross_margin_ratio)

# interest expense to operating margin
if interest_expense:
    buffet_criterias += 1
    interest_expense_to_operating_margin_ratio = interest_expense * 100 / operating_income
    if interest_expense_to_operating_margin_ratio < 15:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('The interest expense is lower than') + ' 15% ({:.2f}%)'.format(interest_expense_to_operating_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + tr('The interest expense is higher than') + ' 15% ({:.2f}%)'.format(interest_expense_to_operating_margin_ratio)
    
# earnings trend
buffet_criterias += 1
slater_criterias += 1
earnings_growth = 0
consistent_growth = True
for i in reversed(range(1, len(income_statements)-1)):
    sign = +1
    if income_statements[i-1]['netIncome']['raw'] > income_statements[i]['netIncome']['raw']:
        sign = -1
    earnings_growth += sign * (1 - (income_statements[i-1]['netIncome']['raw'] / income_statements[i]['netIncome']['raw'])) * 100
    if earnings_growth < 15:
        consistent_growth = False
earnings_growth /= len(income_statements)
if earnings_growth > 0:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + tr('The net earnings follow an upward trend over a period of') + (' {} ' + tr('years') + ' ({:.2f}%)').format(len(income_statements), earnings_growth)
else:
    buffet_not_approved_summary += '\n-' + tr('The net earnings follow a downward trend over a period of') + (' {} ' + tr('years') + ' ({:.2f}%)').format(len(income_statements), earnings_growth)
if earnings_growth > 15:
    slater_approved += 1
    slater_approved_summary += '\n-' + tr('The annual earnings growth rate is higher than') + ' 15% ({:.2f}%)'.format(earnings_growth)
else:
    slater_not_approved_summary += '\n-' + tr('The annual earnings growth rate is lower than') + ' 15% ({:.2f}%)'.format(earnings_growth)
    
# cash and cash equivalents
buffet_criterias += 1
cash_growth = 0
for i in range(len(annual_cash_and_cash_equivalents)-1):
    cash_growth += (1 - (annual_cash_and_cash_equivalents[i]['reportedValue']['raw'] / annual_cash_and_cash_equivalents[i+1]['reportedValue']['raw'])) * 100
    cash_growth /= len(annual_cash_and_cash_equivalents)
if cash_growth > 0:
    buffet_approved += 1
    # todo: check if it's generated by free cash flow
    buffet_approved_summary += '\n-' + tr('The company has a significant amount of cash which increases by') + ' {:.2f}% '.format(cash_growth) + tr('on average per year')
else:
    buffet_not_approved_summary += '\n-' + tr('The company draws on it\'s cash')

# little to no debt
if long_term_debt:
    buffet_criterias += 1
    long_term_debt_to_net_income_ratio = long_term_debt / net_income
    if long_term_debt_to_net_income_ratio < 4:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('The company is in a strong position, its long-term debt to net income ratio is less than') + ' 4 ({:.2f})'.format(long_term_debt_to_net_income_ratio)
    else:
        buffet_not_approved_summary += '\n-' + tr('The company is not in a strong position, its long-term debt to net income ratio is greater than') + ' 4 ({:.2f})'.format(long_term_debt_to_net_income_ratio)

# inventory trend
inventory = balance_sheet['timeSeries']['annualInventory']
if len(inventory) > 0:
    buffet_criterias += 1
    inline_with_each_other = True
    for i in range(len(inventory)-1):
        if inventory[i] == None:
            continue
        earnings_growth = (1 - (income_statements[len(inventory)-1-i]['netIncome']['raw'] / income_statements[len(inventory)-1-i-1]['netIncome']['raw'])) * 100
        inventory_growth = (1 - (inventory[i]['reportedValue']['raw'] / (inventory[i+1]['reportedValue']['raw'] + np.finfo(float).eps))) * 100
        if np.sign(earnings_growth) != np.sign(inventory_growth):
            inline_with_each_other = False
            break
    if inline_with_each_other:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('Inventories move in line with profits')
    else:
        buffet_not_approved_summary += '\n-' + tr('Inventories do not move in line with profits (to be taken into account only if the products sold may become obsolete)')

# ppe
if property_plant_equipment:
    buffet_criterias += 1
    property_to_net_income_ratio = property_plant_equipment / net_income
    if property_to_net_income_ratio < 2:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('Tangible fixed assets (PPE) are reasonable: the tangible fixed assets to net income ratio is less than') + ' 2 ({:.2f})'.format(property_to_net_income_ratio)
    else:
        buffet_not_approved_summary += '\n-' + tr('The tangible fixed assets (PPE) are not very reasonable: the tangible fixed assets to net income ratio is greater than') + ' 2 ({:.2f})'.format(property_to_net_income_ratio)

# # goodwill + intangible assets
# buffet_criterias += 1
# print('% = {}'.format(((goodwill + intangible_assets) * 100) / enterprise_value))

# capex
if capital_expenditures:
    buffet_criterias += 1
    capital_expenditures_to_profit_ratio = np.abs(capital_expenditures, dtype=np.int64) * 100 / net_income
    if capital_expenditures_to_profit_ratio < 50:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + tr('Capital expenditures are reasonable, they represent less than 50% of the net income') + ' ({:.2f}%)'.format(capital_expenditures_to_profit_ratio)
    else:
        buffet_not_approved_summary += '\n-' + tr('Capital expenditures are not very reasonable, they represent more than 50% of the net income') + ' ({:.2f}%)'.format(capital_expenditures_to_profit_ratio)

# results
if buffet_approved / buffet_criterias >= 0.5 and buffet_approved / buffet_criterias <= 0.7:
    print('\n' + tr('The stock value of') + ' {} '.format(company_name) + tr('meets some of Warren Buffet\'s selection criteria'))
elif buffet_approved / buffet_criterias > 0.7:
    print('\n' + tr('The stock value of') + ' {} '.format(company_name) + tr('meets most of Warren Buffet\'s selection criteria'))
else:
    print('\n' + tr('The stock value of') + ' {} '.format(company_name) + tr('does not meet Warren Buffet\'s selection criteria'))
print('\n' + tr('Recommendation') + ' {:.2f}/10'.format(buffet_approved * 10 / buffet_criterias))
print(tr('Pros') + ': {}'.format(buffet_approved_summary))
print(tr('Cons') + ': {}'.format(buffet_not_approved_summary))

if slater_approved / slater_criterias > 0.5 and slater_approved / slater_criterias < 0.7:
    print('\n' + tr('The stock value of') + ' {} '.format(company_name) + tr('meets some of Jim Slater\'s selection criteria'))
elif slater_approved / slater_criterias > 0.7:
    print('\n' + tr('The stock value of') + ' {} '.format(company_name) + tr('meets most of Jim Slater\'s selection criteria'))
else:
    print('\n' + tr('The stock value of') + ' {} '.format(company_name) + tr('does not meet Jim Slater\'s selection criteria'))
print('\n' + tr('Recommendation') + ' {:.2f}/10'.format(slater_approved * 10 / slater_criterias))
print(tr('Pros') + ': {}'.format(slater_approved_summary))
print(tr('Cons') + ': {}'.format(slater_not_approved_summary))

if mayer_approved / mayer_criterias > 0.5 and mayer_approved / mayer_criterias < 0.7:
    print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets some of Chris Mayer\'s selection criteria"))
elif mayer_approved / mayer_criterias > 0.7:
    print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets most of Chris Mayer\'s selection criteria"))
else:
    print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("does not meet Chris Mayer\'s selection criteria"))
print("\n" + tr('Recommendation') + " {:.2f}/10".format(mayer_approved * 10 / mayer_criterias))
print(tr("Pros") + ": {}".format(mayer_approved_summary))
print(tr("Cons") + ": {}".format(mayer_not_approved_summary))
