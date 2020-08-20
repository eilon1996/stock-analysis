import mysql.connector
import mysql
import finance_product
import stock
import etf
import calculation
import numpy as np


class DatabaseHandler:

    def __init__(self):
        ####Isreal you will need to set the details that match your sql user####
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="eilon",
            password="12qwaszx",
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
                user="eilon",
                password="12qwaszx",
                database="mydatabase")
        self.mycursor = self.mydb.cursor()

    def create_table(self):
        try:
            self.mycursor.execute(
                "CREATE TABLE products (symbol VARCHAR(255) PRIMARY KEY, name VARCHAR(255), type VARCHAR(255),"
                " price FLOAT, yield_y5 FLOAT, yield_1y FLOAT, dividend FLOAT, pe_ratio FLOAT ,"
                " profit FLOAT, debt_percentage FLOAT, market_cap BIGINT, "
                "main_sector INT, avg_volume INT, borsa INT, analyst_score INT)")
        except mysql.connector.errors.ProgrammingError:
            print("Table 'products' already exists")

    # should match the update def, but maybe the first def will do

    def extract_values(self, product):
        values = [product.symbol, product.full_name, " ", str(product.price),
                  str(calculation.two_point_percentage(product.yield_5y)),
                  str(calculation.two_point_percentage(product.yield_1y)),
                  str(calculation.two_point_percentage(
                      product.yearly_dividend_per_share[0])),
                  str(product.pe_ratio)]
        if type(product.product) == stock.Stock:
            values[2] = "0"
            values.extend([str(product.product.profitability), str(product.product.debt_percentage),
                           str(product.product.market_cap), str(product.product.main_sector)])
        else:
            values[2] = "1"
            values.extend(
                ["-1.0", "-1.0", "-1.0", str(product.product.main_sector)])

        values.extend([str(self.get_borsa_index(product.borsa)), str(
            product.avg_volume), str(product.analyst_score)])

        return values

    def is_exist(self, product: finance_product, symbol: str = None):
        if symbol is None:
            symbol = product.symbol
        res = self.get_product_by_symbol(symbol)
        return res is not None and len(res) > 0

    def add_product(self, product):
        if self.is_exist(product):
            self.update_row(product)
            return

        sql = "INSERT INTO products (symbol, name, type, price, yield_y5, yield_1y, dividend, pe_ratio, " \
              "profit, debt_percentage, market_cap, main_sector, borsa, avg_volume, analyst_score) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        values = self.extract_values(product)
        self.mycursor.execute(sql, values)
        self.mydb.commit()
        """
        try:
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            # mysql.connector.errors.IntegrityError
        except Exception as e:
            print("database_handler line 101: "+ str(e))
            raise Exception
        """
        # if we want to insert several rows together mycursor.executemany(sql, values.p)

    def add_column(self, product, column_name, col_type=""):

        self.mycursor.execute(
            "ALTER TABLE products ADD COLUMN " + column_name + col_type)

    def update_row(self, product):
        values = self.extract_values(product)

        sql = "UPDATE products (name, type, price, yield_y5, yield_1y, dividend, pe_ratio, " \
            "profit, debt_percentage, market_cap, main_sector, borsa, avg_volume, analyst_score) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
            "WHERE symbol = '" + str(values[0]) + "'"

        self.mycursor.execute(sql, values[1:])
        self.mydb.commit()

        # print(self.mycursor.rowcount, "record(s) affected")

    def show_data(self, data):
        res = np.vstack((calculation.headlines, data))
        print(res)

    def get_all_products(self, limit=None, print=False):

        sql = "SELECT * FROM products"
        if limit is not None:
            sql += " LIMIT " + limit
        self.mycursor.execute(sql)
        data = self.mycursor.fetchall()
        if print:
            self.show_data(data)

        return data

        # self.show_data(myresult)
        # for x in myresult:
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
        sql = "SELECT * FROM products ORDER BY " + column_name
        if reverse:
            sql += " DESC"
        self.mycursor.execute(sql)

        # adding "DESC" at the end will sort in reverse
        # sql = "SELECT * FROM customers ORDER BY name DESC"

    def delete_products(self, where=""):
        if where == "":
            sql = "DROP TABLE IF EXISTS products"
        else:
            sql = "DELETE FROM products WHERE "+where
        self.mycursor.execute(sql)
        self.mydb.commit()

    def create_borsas(self):
        # try:
        self.mycursor.execute(
            "CREATE TABLE borsas (id INT NOT NULL AUTO_INCREMENT, borsa_name VARCHAR(255), PRIMARY KEY (id))")
        return True
        # except mysql.connector.errors.ProgrammingError:
        #print("Table 'borsas' already exists")
        # return False

    def get_borsa_index(self, borsa_name):
        try:
            borsa_name = borsa_name.lower()
            sql = "SELECT * FROM borsas WHERE borsa_name = %s"
            self.mycursor.execute(sql, (borsa_name,))
            res = self.mycursor.fetchone()
        except Exception as e:
            # if the table doesnt exist create it and start again, else raise a problem
            if self.create_borsas():
                self.get_borsa_index(borsa_name)
            else:
                print("cant add new borsa name \n " + str(e))
                raise Exception

        if res is None or len(res) == 0:
            # if the borsa name not found we add it to the database and call the function again
            sql = "INSERT INTO borsas (borsa_name) VALUES (%s)"
            self.mycursor.execute(sql, (borsa_name,))
            self.mydb.commit()
            return self.get_borsa_index(borsa_name)
        else:
            return res[0]

    def get_borsa_name(self, index):
        sql = "SELECT * FROM borsas WHERE id = %s"
        self.mycursor.execute(sql, (index,))
        res = self.mycursor.fetchone()[1]

    # not relevante yet

    def show_tables_names(self):
        self.mycursor.execute("SHOW TABLES")
        for x in self.mycursor:
            print(x)

    def add_comment(self, comment):

        self.mycursor.execute("SHOW TABLES")
        table_exist = False
        for x in self.mycursor:
            if "comments" == x:
                table_exist = True
        if not table_exist:
            self.mycursor.execute(
                "CREATE TABLE comments (id INT PRIMARY KEY, comment VARCHAR(255))")

        sql = "INSERT INTO comments (comment) VALUES (%s)"
        self.mycursor.execute(sql, comment)
        self.mydb.commit()

    def select_column(self):
        self.mycursor.execute("SELECT name FROM products")
        # to fetch only the first row and not all column we use mycursor.fetchone()
        myresult = self.mycursor.fetchall()

        for x in myresult:
            print(x)

        # incase of "errors.InternalError("Unread result found")" will raise
        # we use this except

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

    #for self check
    db = DatabaseHandler()
    db.delete_products()
    db.create_table()
    db.add_product(finance_product.FinanceProduct("msft"))
    print("msft done")
    db.add_product(finance_product.FinanceProduct("qqq"))
    print("qqq done")
    db.add_product(finance_product.FinanceProduct("ma"))
    print("ma done")
    data = db.get_all_products(print=True)
    print("done")
