import argparse
import json
import os
import urllib.request
import requests
import numpy as np
import gettext
from tabulate import tabulate
from utils.millify import millify
from utils.scrappers.investing_dot_com import equities


def printv(msg):
    if args.verbose:
        print(msg)


parser = argparse.ArgumentParser(description='Perform a fundamental analysis of a compagny')
parser.add_argument('symbol', type=str, help='The company symbol')
parser.add_argument('-k', '--apikey', type=str, help='API key')
parser.add_argument('-u', '--update', action='store_true', default=False,
                    help='Update cached company data')
parser.add_argument('-l', '--locale', default='en',
                    help='Language')                    
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Show additional traces')

args = parser.parse_args()

_ = gettext.gettext
if not args.locale == 'en':    
    if args.locale == 'fr':
        fr = gettext.translation('fr_FR', localedir='locales', languages=['fr'])
        fr.install()
        _ = fr.gettext
    else:
        print(_('The specified language was not found, the default language will be used'))

# fetch api key(s)
apikeys = []
if args.apikey:
    apikeys.append(args.apikey)
else:
    keys_dir = './keys'
    if not os.path.exists(keys_dir):
        printv('Creating keys directory')
        os.mkdir(keys_dir)
        print(_('No keys found, please provide an API key or create an empty file and name it with the API key and place you key in key(s) under <keys> directory'))
        exit(0)
    for file in os.listdir(keys_dir):
        apikeys.append(file)
update = args.update

# convert company symbol to uppercase
symbol = args.symbol.upper()

# create cache directory if it doesn't exit
cache_dir = './cache'
if not os.path.exists(cache_dir):
    printv('Creating cache folder')
    os.mkdir(cache_dir)

filename = os.path.join(cache_dir, symbol + '.json')
if not os.path.exists(filename):
    update = True

data = []
if update:
    # fetch company's data
    print(_('Downloading the company\'s data...'))
    # fetch company's financials
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-financials"
    querystring = {"symbol": symbol}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': apikeys[0]
    }
    response = requests.request("GET", url, headers=headers, params=querystring,)
    if not response:
        print(_('The company\'s financial data could not be downloaded for the following reason') +': ', response.reason)
    else:
        data.append(response.json())
    # fetch company's balance-sheet
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-balance-sheet"
    response = requests.request("GET", url, headers=headers, params=querystring,)
    if not response:
        print(_('The company\'s balance-sheet data could not be downloaded for the following reason') +': ', response.reason)
    else:
        data.append(response.json())
    if data:
        print(_('Successfuly downloaded the company\'s data'))
        # store company's data as json
        outfile = open(filename, 'w')
        json.dump(data, outfile, indent=4)
else:
    print(_('Loading cached company\'s data...'))
    infile = open(filename)
    data = json.load(infile)
    print(_('Successfuly loaded cached company\'s data'))

print('\n')

### exctract infos
financials = data[0]
company_name = financials['quoteType']['longName']
if len(financials['summaryDetail']['marketCap']) > 0:
    market_cap = financials['summaryDetail']['marketCap']['raw']
else:
    market_cap = equities.balance_sheet(symbol).total_common_shares_outstanding() * financials['price']['regularMarketOpen']['raw']

## income statement
income_statements = financials['incomeStatementHistory']['incomeStatementHistory']
if 'totalRevenue' in income_statements[0]:
    revenue = income_statements[0]['totalRevenue']['raw']
else:
    revenue = None
    printv('WARNING: Revenue value could not be found')

ebit = income_statements[0]['ebit']['raw']
earnings = income_statements[0]['netIncome']['raw']
# net_income_applicable_to_common_shares = income_statements[0]['netIncomeApplicableToCommonShares']['raw']
gross_profit = income_statements[0]['grossProfit']['raw']
operating_income = income_statements[0]['operatingIncome']['raw']
net_income = income_statements[0]['netIncome']['raw']

# interest expense
if len(income_statements[0]['interestExpense']) > 0:
    interest_expense = income_statements[0]['interestExpense']['raw']
elif len(financials['timeSeries']['annualInterestExpense']) > 0:
    annual_interest_expense = financials['timeSeries']['annualInterestExpense']
    if annual_interest_expense[-1]:
        interest_expense = annual_interest_expense[-1]['reportedValue']['raw']
    else:
        interest_expense = None
        printv('WARNING: Interest expense value could not be found')
else:
    interest_expense = None
    printv('WARNING: Interest expense value could not be found')

if len(income_statements[0]['sellingGeneralAdministrative']) > 0:
    sga = income_statements[0]['sellingGeneralAdministrative']['raw']
else:
    sga = None
    printv('WARNING: SG&A value could not be found')

operating_expense = income_statements[0]['totalOperatingExpenses']['raw']

annual_ebitda = financials['timeSeries']['annualEbitda']
if len(annual_ebitda) > 0:
    ebitda = annual_ebitda[-1]['reportedValue']['raw']
else:
    ebitda = None
    printv('WARNING: EBITDA value could not be found')

## balance-sheet
balance_sheet = data[1]
balance_sheet_statements = balance_sheet['balanceSheetHistory']['balanceSheetStatements']
# common_shares = balance_sheet_statements[0]['commonStock']['raw']
total_assets = balance_sheet_statements[0]['totalAssets']['raw']
stockholder_equity =  balance_sheet_statements[0]['totalStockholderEquity']['raw']

if 'propertyPlantEquipment' in balance_sheet_statements[0]:
    property_plant_equipment = balance_sheet_statements[0]['propertyPlantEquipment']['raw']
else:
    property_plant_equipment = None
    printv('WARNING: Property Plant Equipment value could not be found')

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
        printv('WARNING: Annual long term debt value could not be found')

annual_cash_and_cash_equivalents = balance_sheet['timeSeries']['annualCashAndCashEquivalents']
if len(annual_cash_and_cash_equivalents) > 0 and annual_cash_and_cash_equivalents[-1]:
    cash_and_cash_equivalents = annual_cash_and_cash_equivalents[-1]['reportedValue']['raw']
else:
    cash_and_cash_equivalents = None
    printv('WARNING: Cash and cash equivalents value could not be found')

annual_other_short_term_investments = balance_sheet['timeSeries']['annualOtherShortTermInvestments']
if len(annual_other_short_term_investments) > 0 and annual_other_short_term_investments[-1]:
    other_short_term_investments = annual_other_short_term_investments[-1]['reportedValue']['raw']
else:
    other_short_term_investments = None
    printv('WARNING: Other short term investments value could not be found')

annual_accounts_receivable = balance_sheet['timeSeries']['annualAccountsReceivable']
if len(annual_accounts_receivable) > 0 and annual_accounts_receivable[-1]:
    accounts_receivable = annual_accounts_receivable[-1]['reportedValue']['raw']
else:
    accounts_receivable = None
    printv('WARNING: Accounts receivable value could not be found')

# goodwill = balance_sheet['timeSeries']['annualGoodwill'][-1]['reportedValue']['raw']

annual_current_debt = balance_sheet['timeSeries']['annualCurrentDebt']
if len(annual_current_debt) > 0 and annual_current_debt[-1]:
    short_term_debt = annual_current_debt[-1]['reportedValue']['raw']
else:
    short_term_debt = None
    printv('WARNING: Annual current debt value could not be found')

## cash flow
cash_flow = financials['cashflowStatementHistory']['cashflowStatements']

if 'capitalExpenditures' in cash_flow[0]:
    capital_expenditures = cash_flow[0]['capitalExpenditures']['raw']
elif 'capitalExpenditures' in cash_flow[1]:
    capital_expenditures = cash_flow[1]['capitalExpenditures']['raw']
else:
    capital_expenditures = None
    printv('WARNING: Capital expenditures value could not be found')

if 'depreciation' in cash_flow[0]:
    depreciation = cash_flow[0]['depreciation']['raw']
elif 'depreciation' in cash_flow[1]:
    depreciation = cash_flow[1]['depreciation']['raw']
else:
    depreciation = None
    printv('WARNING: Depreciation value could not be found')

buffet_approved = 0
buffet_criterias = 0
buffet_approved_summary = ''
buffet_not_approved_summary = ''

slater_approved = 0
slater_criterias = 0
slater_approved_summary = ''
slater_not_approved_summary = ''

print('\n' + _('Fundamental analysis of') + ' {} :\n'.format(company_name))

# predict next year earnings using linear regression
l = len(income_statements)
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
printv('\n* ' + _('Change in net income') + ':\n\n+' + tabulate([earnings_table], headers=earnings_table_headers) + '\n')

## market cap
if market_cap:
    slater_criterias += 1
    if market_cap > 300e6 and market_cap < 2e9:
        slater_approved += 1
        slater_approved_summary += '\n-' + _('Slater likes smallcaps')
    else:
        slater_not_approved_summary += '\n-' + _('Slater prefers smallcaps')

## profitability
printv(_('Profitability') + ':')

# gross margin
gross_margin = gross_profit / revenue * 100
buffet_criterias += 1
if gross_margin > 40:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The gross margin is higher than') + ' 40% ({:.2f}%)'.format(gross_margin)
else:
    buffet_not_approved_summary += '\n-' + _('The gross margin is lower than') + ' 40% ({:.2f}%)'.format(gross_margin)
printv(_('Gross margin') + ' (TTM): {:.2f}%'.format(gross_margin))

# operating margin
operating_margin = operating_income / revenue * 100
printv(_('Operating margin') + ' (TTM): {:.2f}%'.format(operating_margin))

# net margin
net_margin = net_income / revenue * 100
buffet_criterias += 1
if net_margin > 20:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The net margin is higher than') + ' 20% ({:.2f}%)'.format(net_margin)
else:
    buffet_not_approved_summary += '\n-' + _('The net margin is lower than') + ' 20% ({:.2f}%)'.format(net_margin)
printv(_('Net margin') + ' (TTM): {:.2f}%'.format(net_margin))

## overall financial performance
printv('\n' + _('Overral financial performance') + ':')

if short_term_debt and long_term_debt and market_cap:
    # ev / ebitda ratio
    if cash_and_cash_equivalents and ebitda:
        total_debt =  short_term_debt + long_term_debt
        enterprise_value = market_cap + total_debt - cash_and_cash_equivalents
        ev_ebitda_ratio = enterprise_value / ebitda
        comment = _('bad')
        if ev_ebitda_ratio < 11:
            comment = _('excellent')
        elif ev_ebitda_ratio < 14:
            comment = _('good')
        printv('EV/EBITDA: {:.2f} -> {}'.format(enterprise_value / ebitda, comment))

    # ebit / ev multiple
    ebit_ev_multiple = ebit / enterprise_value
    printv('EBIT/EV: {:.2f}x'.format(ebit_ev_multiple))

# # eps
# basic_eps = net_income_applicable_to_common_shares / common_shares
# printv('EPS: {}'.format(basic_eps))

## management effectivness
printv('\n' + _('Management effectivness') + ':')
# roa
roa = net_income / total_assets * 100
comment = _('bad')
if roa > 5:
    comment = _('good')
if roa > 10:
    comment = _('excellent')
printv('ROA (TTM): {:.2f}% -> {}'.format(roa, comment))

# roce (return on capital employed)
slater_criterias += 1
capital_employed = total_assets - current_liabilities
roce = ebit / capital_employed * 100
comment = '...'
if roce > 20:
    comment = _('excellent')
    slater_approved += 1
    slater_approved_summary += '\n-' + _('The return on capital employed is higher than') + ' 20% ({:.2f}%)'.format(roce)
else:
    slater_not_approved_summary += '\n-' + _('The return on capital employed is lower than') + ' 20% ({:.2f}%)'.format(roce)
printv('ROCE (TTM): {:.2f}% -> {}'.format(roce, comment))

# roe
roe = net_income / stockholder_equity * 100
comment = _('bad')
if roe >= 15 and roe <= 20:
    comment = _('good')
elif roe > 20:
    comment = _('excellent')
printv('ROE (TTM): {:.2f}% -> {}'.format(roe, comment))

## balance sheet
printv('\n' + _('Balance sheet') + ':')

# current ratio
buffet_criterias += 1
current_ratio = current_assets / current_liabilities
if current_ratio > 1.5:
    comment = _('good')
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The current ratio is higher than') + ' 1.5 ({:.2f})'.format(current_ratio)
    if (current_ratio > 2.5):
        buffet_approved_summary += '\n-' + _('However, you should note that the current ratio is higher than') + ' 2.5, ' + _('which may indicate mismanagement of money due to an inability to collect payments')
else:
    comment = _('bad')
    buffet_not_approved_summary += '\n-' + _('The current ratio is lower than') + ' 1.5 ({:.2f})'.format(current_ratio)
    if current_ratio < 1:
        comment = _('very bad')
        buffet_not_approved_summary += '\n-' + _('The company must acquire new debt to pay its debt obligations')
printv(_('Current ratio') + ' (TTM): {:.2f} -> {}'.format(current_ratio, comment))

# quick ratio
if other_short_term_investments and accounts_receivable and cash_and_cash_equivalents:
    slater_criterias += 1
    quick_ratio = (cash_and_cash_equivalents + other_short_term_investments + accounts_receivable) / current_liabilities
    if quick_ratio > 1:
        slater_approved += 1
        slater_approved_summary += '\n-' + _('The company has good financials, it\'s QR is higher than') + ' 1 ({:.2f})'.format(quick_ratio)
        if quick_ratio <= 1.5:
            comment = _('good')
        elif quick_ratio > 1.5:
            comment = _('excellent')
    else: 
        comment = _('bad')
        slater_not_approved_summary += '\n-' + _('The company doesn\'t have good financials, it\'s QR is lower than') + ' 1 ({:.2f})'.format(quick_ratio)
    printv('QR (TTM): {:.2f} -> {}'.format(quick_ratio, comment))

if sga:
    buffet_criterias += 1
    sga_to_gross_margin_ratio = sga * 100 / gross_profit
    if sga_to_gross_margin_ratio < 30:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('Selling, General and Administrative expenses represent less than 30% of the gross margin') + ' ({:.2f}%)'.format(sga_to_gross_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('Selling, General and Administrative expenses represent more than 30% of the gross margin') + ' ({:.2f}%)'.format(sga_to_gross_margin_ratio)
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
        buffet_approved_summary += '\n-' + _('The depreciation is low') + ' ({:.2f}%)'.format(depreciation_to_gross_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('The depreciation is high') + ' ({:.2f}%)'.format(depreciation_to_gross_margin_ratio)

# interest expense to operating margin
if interest_expense:
    buffet_criterias += 1
    interest_expense_to_operating_margin_ratio = interest_expense * 100 / operating_income
    if interest_expense_to_operating_margin_ratio < 15:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('The interest expense is lower than') + ' 15% ({:.2f}%)'.format(interest_expense_to_operating_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('The interest expense is higher than') + ' 15% ({:.2f}%)'.format(interest_expense_to_operating_margin_ratio)
    
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
    buffet_approved_summary += '\n-' + _('The net earnings follow an upward trend over a period of') + (' {} ' + _('years') + ' ({:.2f}%)').format(len(income_statements), earnings_growth)
else:
    buffet_not_approved_summary += '\n-' + _('The net earnings follow a downward trend over a period of') + (' {} ' + _('years') + ' ({:.2f}%)').format(len(income_statements), earnings_growth)
if earnings_growth > 15:
    slater_approved += 1
    slater_approved_summary += '\n-' + _('The annual earnings growth rate is higher than') + ' 15% ({:.2f}%)'.format(earnings_growth)
else:
    slater_not_approved_summary += '\n-' + _('The annual earnings growth rate is lower than') + ' 15% ({:.2f}%)'.format(earnings_growth)
    
# cash and cash equivalents
buffet_criterias += 1
cash_growth = 0
for i in range(len(annual_cash_and_cash_equivalents)-1):
    cash_growth += (1 - (annual_cash_and_cash_equivalents[i]['reportedValue']['raw'] / annual_cash_and_cash_equivalents[i+1]['reportedValue']['raw'])) * 100
    cash_growth /= len(annual_cash_and_cash_equivalents)
if cash_growth > 0:
    buffet_approved += 1
    # todo: check if it's generated by free cash flow
    buffet_approved_summary += '\n-' + _('The company has a significant amount of cash which increases by') + ' {:.2f}% '.format(cash_growth) + _('on average per year')
else:
    buffet_not_approved_summary += '\n-' + _('The company draws on it\'s cash')

# little to no debt
if long_term_debt:
    buffet_criterias += 1
    long_term_debt_to_net_income_ratio = long_term_debt / net_income
    if long_term_debt_to_net_income_ratio < 4:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('The company is in a strong position, its long-term debt to net income ratio is less than') + ' 4 ({:.2f})'.format(long_term_debt_to_net_income_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('The company is not in a strong position, its long-term debt to net income ratio is greater than') + ' 4 ({:.2f})'.format(long_term_debt_to_net_income_ratio)

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
        buffet_approved_summary += '\n-' + _('Inventories move in line with profits')
    else:
        buffet_not_approved_summary += '\n-' + _('Inventories do not move in line with profits (to be taken into account only if the products sold may become obsolete)')

# ppe
if property_plant_equipment:
    buffet_criterias += 1
    property_to_net_income_ratio = property_plant_equipment / net_income
    if property_to_net_income_ratio < 2:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('Tangible fixed assets (PPE) are reasonable: the tangible fixed assets to net income ratio is less than') + ' 2 ({:.2f})'.format(property_to_net_income_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('The tangible fixed assets (PPE) are not very reasonable: the tangible fixed assets to net income ratio is greater than') + ' 2 ({:.2f})'.format(property_to_net_income_ratio)

# # goodwill + intangible assets
# buffet_criterias += 1
# print('% = {}'.format(((goodwill + intangible_assets) * 100) / enterprise_value))

# capex
if capital_expenditures:
    buffet_criterias += 1
    capital_expenditures_to_profit_ratio = np.abs(capital_expenditures, dtype=np.int64) * 100 / net_income
    if capital_expenditures_to_profit_ratio < 50:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('Capital expenditures are reasonable, they represent less than 50% of the net income') + ' ({:.2f}%)'.format(capital_expenditures_to_profit_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('Capital expenditures are not very reasonable, they represent more than 50% of the net income') + ' ({:.2f}%)'.format(capital_expenditures_to_profit_ratio)

# results
if buffet_approved / buffet_criterias >= 0.5 and buffet_approved / buffet_criterias <= 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets some of Warren Buffet\'s selection criteria'))
elif buffet_approved / buffet_criterias > 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets most of Warren Buffet\'s selection criteria'))
else:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('does not meet Warren Buffet\'s selection criteria'))
print('\n' + _('Recommendation') + ' {:.2f}/10'.format(buffet_approved * 10 / buffet_criterias))
print(_('Pros') + ': {}'.format(buffet_approved_summary))
print(_('Cons') + ': {}'.format(buffet_not_approved_summary))

if slater_approved / slater_criterias > 0.5 and slater_approved / slater_criterias < 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets some of Jim Slater\'s selection criteria'))
elif slater_approved / slater_criterias > 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets most of Jim Slater\'s selection criteria'))
else:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('does not meet Jim Slater\'s selection criteria'))
print('\n' + _('Recommendation') + ' {:.2f}/10'.format(slater_approved * 10 / slater_criterias))
print(_('Pros') + ': {}'.format(slater_approved_summary))
print(_('Cons') + ': {}'.format(slater_not_approved_summary))
