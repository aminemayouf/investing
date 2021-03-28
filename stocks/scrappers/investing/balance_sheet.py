
class BalanceSheet:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def __extract(self, label):
        if not label in self.data.index:
            return None
        return self.data.loc[label]

    def total_current_assets(self):
        return self.__extract("Total Current Assets")

    def cash_and_equivalents(self):
        return self.__extract("Cash & Equivalents")
    
    def short_term_investments(self):
        return self.__extract("Short Term Investments")

    def accounts_receivable(self):
        return self.__extract("Accounts Receivables - Trade, Net")

    def total_inventory(self):
        return self.__extract("Total Inventory")

    def total_assets(self):
        return self.__extract("Total Assets")
    
    def total_current_liabilities(self):
        return self.__extract("Total Current Liabilities")

    def short_term_debt(self):
        return self.__extract("Notes Payable/Short Term Debt")

    def total_property_plant_equipment(self):
        return self.__extract("Property/Plant/Equipment, Total - Net")

    def current_debt_and_capital_lease_obligation(self):
        return self.__extract("Current Port. of LT Debt/Capital Leases")

    def total_long_term_debt(self):
        return self.__extract("Total Long Term Debt")

    def total_equity(self):
        return self.__extract("Total Equity")
   
    def total_common_shares_outstanding(self):
        return self.__extract("Total Common Shares Outstanding")
