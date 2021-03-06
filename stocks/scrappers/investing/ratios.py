
class Ratios:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def __extract(self, label):
        if not label in self.data.index:
            return None
        return self.data.loc[label]

    def price_to_sales_ttm(self):
        return self.__extract("Price to Sales TTM")
