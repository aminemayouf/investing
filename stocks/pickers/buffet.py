import config
import numpy as np
from utils.translate import Translator

class Buffet:

    def __init__(self, equity):
        self.equity = equity

    def __safe_get(self, value, index):
        return None if value is None else value[index]

    def evaluation(self):
        # get translator
        tr = Translator(config.language)

        # init
        n_approved = 0
        n_evaluated = 0
        approved_summary = ""
        not_approved_summary = ""

        ##  income statement
        income_statement = self.equity.income_statement

        annual_net_income = income_statement.net_income()
        gross_profit = self.__safe_get(income_statement.gross_profit(), 0)
        interest_expense = self.__safe_get(income_statement.interest_expense(), 0)
        net_income = self.__safe_get(annual_net_income, 0)
        operating_income = self.__safe_get(income_statement.operating_income(), 0)
        revenue = self.__safe_get(income_statement.total_revenue(), 0)
        sga = self.__safe_get(income_statement.selling_general_administrative_expenses(), 0)

        # gross margin
        if gross_profit and revenue:
            n_evaluated += 1
            gross_margin = gross_profit / revenue * 100
            if gross_margin > 40:
                n_approved += 1
                approved_summary += "\n-" + tr("The gross margin is higher than") + " 40% ({:.2f}%)".format(gross_margin)
            else:
                not_approved_summary += "\n-" + tr("The gross margin is lower than") + " 40% ({:.2f}%)".format(gross_margin)

        # net margin
        if net_income and revenue:
            n_evaluated += 1
            net_margin = net_income / revenue * 100
            if net_margin > 20:
                n_approved += 1
                approved_summary += "\n-" + tr("The net margin is higher than") + " 20% ({:.2f}%)".format(net_margin)
            else:
                not_approved_summary += "\n-" + tr("The net margin is lower than") + " 20% ({:.2f}%)".format(net_margin)

        # sga to gross margin
        if sga and gross_profit:
            n_evaluated += 1
            sga_to_gross_margin_ratio = sga * 100 / gross_profit
            if sga_to_gross_margin_ratio < 30:
                n_approved += 1
                approved_summary += "\n-" + tr("Selling, General and Administrative expenses represent less than 30% of the gross margin") + " ({:.2f}%)".format(sga_to_gross_margin_ratio)
            else:
                not_approved_summary += "\n-" + tr("Selling, General and Administrative expenses represent more than 30% of the gross margin") + " ({:.2f}%)".format(sga_to_gross_margin_ratio)

        # interest expense to operating margin
        if interest_expense and operating_income:
            n_evaluated += 1
            interest_expense_to_operating_margin_ratio = interest_expense * 100 / operating_income
            if interest_expense_to_operating_margin_ratio < 15:
                n_approved += 1
                approved_summary += "\n-" + tr("The interest expense is lower than") + " 15% ({:.2f}%)".format(interest_expense_to_operating_margin_ratio)
            else:
                not_approved_summary += "\n-" + tr("The interest expense is higher than") + " 15% ({:.2f}%)".format(interest_expense_to_operating_margin_ratio)

        # earnings trend
        n_evaluated += 1
        earnings_growth = 0
        n = len(annual_net_income)
        for i in reversed(range(1, n-1)):
            sign = +1
            if annual_net_income[i-1] > annual_net_income[i]:
                sign = -1
            earnings_growth += sign * (1 - (annual_net_income[i-1] / annual_net_income[i])) * 100

        earnings_growth /= n
        if earnings_growth > 0:
            n_approved += 1
            approved_summary += "\n-" + tr("The net earnings follow an upward trend over a period of") + (" {} " + tr("years") + " ({:.2f}%)").format(n, earnings_growth)
        else:
            not_approved_summary += "\n-" + tr("The net earnings follow a downward trend over a period of") + (" {} " + tr("years") + " ({:.2f}%)").format(n, earnings_growth)

        ## balance sheet
        balance_sheet = self.equity.balance_sheet

        current_assets = self.__safe_get(balance_sheet.total_current_assets(), 0)
        current_liabilities = self.__safe_get(balance_sheet.total_current_liabilities(), 0)
        long_term_debt = self.__safe_get(balance_sheet.total_long_term_debt(), 0)
        property_plant_equipment = self.__safe_get(balance_sheet.total_property_plant_equipment(), 0)
        annual_inventory = balance_sheet.total_inventory()
        annual_cash_and_equivalents = balance_sheet.cash_and_equivalents()

        # current ratio
        if current_assets and current_liabilities:
            n_evaluated += 1
            current_ratio = current_assets / current_liabilities
            if current_ratio > 1.5:
                n_approved += 1
                approved_summary += "\n-" + tr("The current ratio is higher than") + " 1.5 ({:.2f})".format(current_ratio)
                if (current_ratio > 2.5):
                    approved_summary += "\n-" + tr("However, you should note that the current ratio is higher than") + " 2.5, " + tr("which may indicate mismanagement of money due to an inability to collect payments")
            else:
                not_approved_summary += "\n-" + tr("The current ratio is lower than") + " 1.5 ({:.2f})".format(current_ratio)
                if current_ratio < 1:
                    not_approved_summary += "\n-" + tr("The company must acquire new debt to pay its debt obligations")

        # inventory trend
        if not annual_inventory is None:
            n = len(annual_inventory)
            if n > 0 and n == len(annual_net_income):
                n_evaluated += 1
                inline_with_each_other = True
                for i in range(n-1):
                    if annual_inventory[i] == None:
                        continue
                    earnings_growth = (1 - (annual_net_income[n-1-i] / annual_net_income[n-1-i-1])) * 100
                    inventory_growth = (1 - (annual_inventory[i] / (annual_inventory[i+1] + np.finfo(float).eps))) * 100
                    if np.sign(earnings_growth) != np.sign(inventory_growth):
                        inline_with_each_other = False
                        break
                if inline_with_each_other:
                    n_approved += 1
                    approved_summary += "\n-" + tr("Inventories move in line with profits")
                else:
                    not_approved_summary += "\n-" + tr("Inventories do not move in line with profits (to be taken into account only if the products sold may become obsolete)")

        # ppe
        if property_plant_equipment and net_income:
            n_evaluated += 1
            property_to_net_income_ratio = property_plant_equipment / net_income
            if property_to_net_income_ratio < 2:
                n_approved += 1
                approved_summary += "\n-" + tr("Tangible fixed assets (PPE) are reasonable: the tangible fixed assets to net income ratio is less than") + " 2 ({:.2f})".format(property_to_net_income_ratio)
            else:
                not_approved_summary += "\n-" + tr("The tangible fixed assets (PPE) are not very reasonable: the tangible fixed assets to net income ratio is greater than") + " 2 ({:.2f})".format(property_to_net_income_ratio)

        ## cash flow
        cash_flow = self.equity.cash_flow
        
        capital_expenditures = self.__safe_get(cash_flow.capital_expenditures(), 0)
        depreciation = self.__safe_get(cash_flow.depreciation(), 0)
        
        # depretiation to gross margin
        if depreciation and gross_profit:
            n_evaluated += 1
            depreciation_to_gross_margin_ratio = depreciation * 100 / gross_profit
            if depreciation_to_gross_margin_ratio < 15:
                n_approved += 1
                approved_summary += "\n-" + tr("The depreciation is low") + " ({:.2f}%)".format(depreciation_to_gross_margin_ratio)
            else:
                not_approved_summary += "\n-" + tr("The depreciation is high") + " ({:.2f}%)".format(depreciation_to_gross_margin_ratio)

        # cash and cash equivalents
        if not annual_cash_and_equivalents is None:
            n_evaluated += 1
            cash_growth = 0
            n = len(annual_cash_and_equivalents)
            for i in range(n-1):
                cash_growth += (1 - (balance_sheet.cash_and_equivalents()[i] / balance_sheet.cash_and_equivalents()[i+1])) * 100
                cash_growth /= n
            if cash_growth > 0:
                n_approved += 1
                # todo: check if it"s generated by free cash flow
                approved_summary += "\n-" + tr("The company has a significant amount of cash which increases by") + " {:.2f}% ".format(cash_growth) + tr("on average per year")
            else:
                not_approved_summary += "\n-" + tr("The company draws on it's cash")

        # little to no debt
        if long_term_debt and net_income:
            n_evaluated += 1
            long_term_debt_to_net_income_ratio = long_term_debt / net_income
            if long_term_debt_to_net_income_ratio < 4:
                n_approved += 1
                approved_summary += "\n-" + tr("The company is in a strong position, its long-term debt to net income ratio is less than") + " 4 ({:.2f})".format(long_term_debt_to_net_income_ratio)
            else:
                not_approved_summary += "\n-" + tr("The company is not in a strong position, its long-term debt to net income ratio is greater than") + " 4 ({:.2f})".format(long_term_debt_to_net_income_ratio)

        # capex
        if capital_expenditures and net_income:
            n_evaluated += 1
            capital_expenditures_to_profit_ratio = np.abs(capital_expenditures, dtype=np.float64) * 100 / net_income
            if capital_expenditures_to_profit_ratio < 50:
                n_approved += 1
                approved_summary += "\n-" + tr("Capital expenditures are reasonable, they represent less than 50% of the net income") + " ({:.2f}%)".format(capital_expenditures_to_profit_ratio)
            else:
                not_approved_summary += "\n-" + tr("Capital expenditures are not very reasonable, they represent more than 50% of the net income") + " ({:.2f}%)".format(capital_expenditures_to_profit_ratio)

        ### results
        if n_evaluated > 0:
            company_name = self.equity.name
            if n_approved / n_evaluated >= 0.5 and n_approved / n_evaluated <= 0.7:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets some of Warren Buffet\'s selection criteria"))
            elif n_approved / n_evaluated > 0.7:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets most of Warren Buffet\'s selection criteria"))
            else:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("does not meet Warren Buffet\'s selection criteria"))
            print("\n" + tr("Recommendation") + " {:.2f}/10".format(n_approved * 10 / n_evaluated))
            print(tr("Pros") + ": {}".format(approved_summary))
            print(tr("Cons") + ": {}".format(not_approved_summary))