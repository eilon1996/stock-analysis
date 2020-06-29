from finance_product import FinanceProduct


class Stock(FinanceProduct):

    def __init__(self, symbol, market_cap):
        self.symbol = symbol
        self.market_cap = market_cap
        data = self.get_revenue_n_net_income()
        self.revenue = data["revenue"]
        self.income = data["income"]
        data = self.get_assent_n_debt()
        self.assents = data["assents"]
        self.debt = data["debt"]
        self.free_cash = self.get_free_cash()

    def get_revenue_n_net_income(self):
        """"get the stock name and return 2 diamention list with the last 4 years data"""

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/financials?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "D(tbrg)"})
        data_content_revenue_income = [data.contents[0], data.contents[10]]
        revenue = data_content_revenue_income[0].contents[0].contents
        revenue_value = [convert_string_to_number(x.string) for x in revenue[2:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-201
        income_net = data_content_revenue_income[1].contents[0].contents
        income_net_value = [convert_string_to_number(x.string) for x in income_net[2:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-2016
        # print(revenue_value, income_net_value)
        return [revenue_value, income_net_value]


    def get_assent_n_debt(self):
        """"get the stock name and return 2 diamention list with the last 4 years data"""

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/balance-sheet?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "D(tbrg)"})
        data_content_assent_debt = [data.contents[0], data.contents[11]]
        assent = data_content_assent_debt[0].contents[0].contents
        assent_value = [convert_string_to_number(x.string) for x in assent[1:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-201
        debt = data_content_assent_debt[1].contents[0].contents
        debt_value = [convert_string_to_number(x.string) for x in debt[1:]]   # in 0 get the title 1 is not important the rest are the values per year 2019-2016
        return [assent_value, debt_value]

    def get_free_cash(self):
        """"get the stock name and return 2 diamention list with the last 4 years data"""
        url = "https://finance.yahoo.com/quote/"+self.symbol+"/cash-flow?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
        free_cash_value = [convert_string_to_number(x.text) for x in data]
        return free_cash_value


