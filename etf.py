from finance_product import FinanceProduct


class Etf(FinanceProduct):

    def __init__(self, symbol, expense_ratio):
        self.symbol = symbol
        self.expense_ratio = expense_ratio
        self.holdings = self.get_holdings() # a nested tuple ((1th_stock, percentage) ... )



    def get_etf_profile(self): # TODO everything
        """"get the stock name and return 2 diamention list with the last 4 years data"""
        url = "https://etfdb.com/etf/"+self.symbol+"/#etf-ticker-profile"
        soup = BeautifulSoup(requests.get(url).text, "lxml")      # Parse the html content ( # Make a GET request to fetch the raw HTML content , )
        data = soup.find("div", attrs={"class": "D(tbrg)"}).contents[14].contents[0].contents[2:]
        free_cash_value = [convert_string_to_number(x.text) for x in data]
        return free_cash_value

    def get_holdings(self):
        """"get the stock name and return avg' volume, PE ratio, yearly dividend"""

        url = "https://finance.yahoo.com/quote/"+self.symbol+"/holdings?p="+self.symbol
        html_content = requests.get(url).text           # Make a GET request to fetch the raw HTML content
        soup = BeautifulSoup(html_content, "lxml")      # Parse the html content
        data = soup.find("section", attrs={"class": "Pb(20px) smartphone_Px(20px) smartphone_Mt(20px)"})

        stocks_share = convert_string_to_number(data.contents[0].contents[0].contents[1].contents[0].contents[1].text[:-1])

        bond_share = convert_string_to_number(data.contents[0].contents[0].contents[1].contents[1].contents[1].text[:-1])

        if bond_share>10:
            bond_sectors_data = data.contents[1].contents[1].contents[1].contents
            bond_sectors = [convert_string_to_number(x.contents[1].text[:-1]) for x in bond_sectors_data[1:]]

        sectors_share_data = data.contents[0].contents[1].contents[1].contents
        sectors_share = [convert_string_to_number(x.contents[2].text[:-1]) for x in sectors_share_data[1:]]

        top_holdings_data = data.contents[3].contents[1].contents[1].contents
        # top holding example [[microsoft corp, MSFT, 11.76], [apple inc, AAPL, 11.09] ... ]
        top_holdings = [[x.contents[0].text, x.contents[1].text, convert_string_to_number(x.contents[2].text[:-1])]for x in top_holdings_data]

        return 1

