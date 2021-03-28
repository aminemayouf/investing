
class IncomeStatement:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def __extract(self, label):
        if not label in self.data.index:
            return None
        return self.data.loc[label]

    def column(self, index):
        return self.data.columns[index]

    def total_revenue(self):
        return self.__extract("Total Revenue")
    
    def gross_profit(self):
        return self.__extract("Gross Profit")
    
    def total_operating_expenses(self):
        return self.__extract("Total Operating Expenses")

    def selling_general_administrative_expenses(self):
        return self.__extract("Selling/General/Admin. Expenses, Total")
    
    def depreciation_amortization(self):
        return self.__extract("Depreciation / Amortization")
    
    def interest_expense(self):
        return self.__extract("Interest Expense (Income) - Net Operating")

    def interest_income(self):
        return self.__extract("Interest Income (Expense), Net Non-Operating")

    def operating_income(self):
        return self.__extract("Operating Income")

    def net_income(self):
        return self.__extract("Net Income")

    def net_income_before_taxes(self):
        return self.__extract("Net Income Before Taxes")
    
    def provision_for_income_taxes(self):
        return self.__extract("Provision for Income Taxes")

    def net_income_after_taxes(self):
        return self.__extract("Net Income After Taxes")

    def income_available_to_common_excluding_extraordinary_items(self):
        return self.__extract("Income Available to Common Excluding Extraordinary Items")