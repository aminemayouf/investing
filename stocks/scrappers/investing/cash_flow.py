class CashFlow:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def __extract(self, label):
        if not label in self.data.index:
            return None
        return self.data.loc[label]

    def depreciation(self):
        return self.__extract("Depreciation/Depletion")
    
    def capital_expenditures(self):
        return self.__extract("Capital Expenditures")