
class Ratios:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def price_to_sales_ttm(self):
        return self.data.loc["Price to Sales TTM"].astype(float)
