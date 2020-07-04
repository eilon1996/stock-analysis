import mysql.connector
import finance_product
import stock
import etf
import calculation
import numpy as np


class DatabaseHandler:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="e12QWaszx",
        )

        # neceserry only for the first time
        try:
            mycursor = self.mydb.cursor()
            mycursor.execute("CREATE DATABASE mydatabase")
            mycursor.execute("USE mydatabase")

        except mysql.connector.errors.DatabaseError:
            # in case database is already exist
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="e12QWaszx",
                database="mydatabase")
        self.mycursor = self.mydb.cursor()

        self.headlines = np.asarray(["symbol", "name", "type", "price", "5 years yield", "one years yield", "pe ratio",
              "profitability", "debt/assents", "market_cap", "top_sector", "country", "average volume", "analyst score"])

    def create_table(self):
        try:
            self.mycursor.execute(
                "CREATE TABLE products (symbol VARCHAR(255) PRIMARY KEY, name VARCHAR(255), type VARCHAR(255),"
                " price FLOAT, yield_y5 FLOAT, yield_1y FLOAT, pe_ratio FLOAT ,"
                " profit FLOAT, debt_percentage FLOAT, market_cap VARCHAR(255), "
                "top_sector VARCHAR(255), avg_volume INT, country VARCHAR(255), analyst_score INT)")
        except mysql.connector.errors.ProgrammingError:
            print("Table 'products' already exists")

    def extract_values(self, product):
        values = [product.symbol, product.full_name, " ", product.price,
                  calculation.two_point_percentage(product.yield_5y),
                  calculation.two_point_percentage(product.yield_1y), product.pe_ratio]
        if type(product.product) == stock.Stock:
            values[2] = "stock"
            values.extend([product.product.profitability, product.product.debt_percentage, product.product.market_cap,
                           "-"])
        else:
            values[2] = "etf"
            values.extend([-1.0, -1.0, -1.0, product.product.top_sector])

        values.extend([product.country, product.avg_volume, product.analyst_score])

        return values

    # should match the update def, but maybe the first def will do
    def extract_values2(self, product):
        values = [product.symbol, product.full_name, " ", str(product.price),
                  str(calculation.two_point_percentage(product.yield_5y)),
                  str(calculation.two_point_percentage(product.yield_1y)), str(product.pe_ratio)]
        if type(product.product) == stock.Stock:
            values[2] = "stock"
            values.extend([str(product.product.profitability), str(product.product.debt_percentage),
                           str(product.product.market_cap),
                           "-"])
        else:
            values[2] = "etf"
            values.extend(["-1.0", "-1.0", "-1.0", product.product.top_sector])

        values.extend([product.country, str(product.avg_volume), str(product.analyst_score)])

        return values

    def is_exist(self, product: finance_product, symbol: str = None):
        if symbol is None:
            symbol = product.symbol
        res = self.get_product_by_symbol(symbol)
        return res is not None and len(res) > 0

    def insert_product(self, product):

        if self.is_exist(product):
            return

        sql = "INSERT INTO products (symbol, name, type, price, yield_y5, yield_1y, pe_ratio, " \
              "profit, debt_percentage, market_cap, top_sector, country, avg_volume, analyst_score) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        values = self.extract_values(product)
        try:
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            # mysql.connector.errors.IntegrityError
        except:
            self.update_row(product)

        # if we want to insert several rows together mycursor.executemany(sql, values.p)

    def add_column(mycursor, tableName, column_name="", col_type=""):
        # TODO set the col_type

        self.mycursor.execute(
            "ALTER TABLE " + tableName + " ADD COLUMN " + column_name + " INT AUTO_INCREMENT PRIMARY KEY")

        sql = "UPDATE product " \
              "SET (name, type, price, yield_y5, yield_1y, pe_ratio, " \
              "profit, debt_percentage, market_cap, top_sector, country, avg_volume, analyst_score) = " \
              "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
              "WHERE symbol = " + product.symbol

    def update_row(self, product):
        values = self.extract_values2(product)

        sql = "UPDATE products " \
              "SET name = '" + values[1] + "', type = '" + values[2] + "', price = " + values[3] + ", yield_y5 = " + \
              values[4] + ", yield_1y = " + values[5] + ", pe_ratio = " + values[6] + ", " \
                                                                                      "profit = " + values[
                  7] + ", debt_percentage = " + values[8] + ", market_cap = " + values[9] + ", top_sector = '" + values[
                  10] + "', country = '" + values[11] + "', avg_volume = " + values[12] + ", analyst_score = " + values[
                  13] + "" \
                        " WHERE symbol = '" + str(values[0]) + "'"

        self.mycursor.execute(sql)
        self.mydb.commit()

        # print(self.mycursor.rowcount, "record(s) affected")

    def show_data(self, data):
        res = np.vstack((self.headlines, data))
        print(res)

    def get_all_products(self, limit=None):

        sql = "SELECT * FROM products"
        if limit is not None:
            sql += " LIMIT " + limit
        self.mycursor.execute(sql)
        return self.mycursor.fetchall()

        #self.show_data(myresult)
        #for x in myresult:
        #    print(x)

    def get_product_by_numeric_param(self, param, min=None, max=None, limit=None):
        sql = "SELECT * FROM products WHERE " + param
        if min is None:
            condition = " <= " + max
        elif max is None:
            condition = " >= " + min
        else:
            condition = " BETWEEN " + min + " AND " + max
        if limit is not None:
            condition += " LIMIT " + limit
        self.mycursor.execute(sql + condition)
        res = self.mycursor.fetchall()

        return res

    def get_product_by_name(self, name, limit=None):
        sql = "SELECT * FROM products WHERE symbol LIKE = %s"
        if limit is not None:
            sql += " LIMIT " + limit
        self.mycursor.execute(sql, "%" + name + "%")
        res = self.mycursor.fetchall()

        return res

    def get_product_by_symbol(self, symbol):
        symbol = symbol.upper()
        sql = "SELECT * FROM products WHERE symbol = %s"
        self.mycursor.execute(sql, (symbol,))
        res = self.mycursor.fetchone()
        return res

        # other options
        # select rows where the address contain "way", the "#" could be also only from one side
        # sql = "SELECT * FROM tablename WHERE address LIKE '%way%'"

        # you can limit the amount of rows selected (to 5) and starting from a certain row (2)
        # self.mycursor.execute("SELECT * FROM customers LIMIT 5 OFFSET 2")

        # mycursor.execute(sql)

        # using changing values

    def sort_table_by(self, column_name, reverse=False):
        sql = "SELECT * FROM tablename ORDER BY " + column_name
        if reverse:
            sql += " DESC"
        self.mycursor.execute(sql)

        # adding "DESC" at the end will sort in reverse
        # sql = "SELECT * FROM customers ORDER BY name DESC"

    def delete(self, table_name="", where=""):
        if table_name == "":
            table_name = "products"
        if where == "":
            sql = "DELETE FROM " + table_name
        else:
            sql = "DELETE FROM products WHERE address = 'Mountain 21'"
        self.mycursor.execute(sql)
        self.mydb.commit()

    def delete_table(self):
        sql = "DROP TABLE IF EXISTS products"
        self.mycursor.execute(sql)

        # if we know for sure that the table exist we can use:
        # sql = "DROP TABLE "+table_name

    # not relevante yet
    def show_tables_names(self):
        self.mycursor.execute("SHOW TABLES")
        for x in mycursor:
            print(x)

    def add_comment(self, comment):

        self.mycursor.execute("SHOW TABLES")
        table_exist = False
        for x in mycursor:
            if "comments" == x:
                table_exist = True
        if not table_exist:
            self.mycursor.execute("CREATE TABLE comments (id INT PRIMARY KEY, comment VARCHAR(255))")

        sql = "INSERT INTO comments (comment) VALUES (%s)"
        self.mycursor.execute(sql, comment)
        self.mydb.commit()


    def select_column(self):
        try:
            mycursor.execute("SELECT name FROM products")
            # to fetch only the first row and not all column we use mycursor.fetchone()
            myresult = mycursor.fetchall()

            for x in myresult:
                print(x)

        # incase of "errors.InternalError("Unread result found")" will raise
        # we use this except
        except mysql.errors.InternalError:
            self.mydb, mycursor = restore_data_base()
            select_all(mycursor)

        # the correct way to do it is by using
        # cursor = cnx.cursor(buffered=True)
        # but this is relevant only when using
        # import mysql.connector
        # cnxn = mysql.connector.connect(
        #     host='127.0.0.1',
        #         user='root',
        #         password='whatever',
        #         database='self.mydb')
        # crsr = cnxn.cursor()



    # you cant use the word "match" for a table name
    # will raise: mysql.connector.errors.ProgrammingError: 1064 (42000): You have an error in your SQL syntax;
    #   check the manual that corresponds to your MySQL server version for the right syntax to use near...


if __name__ == '__main__':
    db = DatabaseHandler()
    db.delete_table()
    db.create_table()
    db.insert_product(finance_product.FinanceProduct("MSFT"))
    db.insert_product(finance_product.FinanceProduct("QLD"))
    db.select_all()
    print("done")
