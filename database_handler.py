import mysql.connector
import mysql
import finance_product
import calculation
import numpy as np


class DatabaseHandler:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="eilon",
            password="12qwaszx",
        )

        try:
            # in case database is already exist
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="eilon",
                password="12qwaszx",
                database="mydatabase")

        except mysql.connector.errors.DatabaseError:
        # neceserry only for the first time
            mycursor = self.mydb.cursor()
            mycursor.execute("CREATE DATABASE mydatabase")
            mycursor.execute("USE mydatabase")

        self.mycursor = self.mydb.cursor()

    def create_table(self):
        try:
            self.mycursor.execute(
                "CREATE TABLE products ("
                "symbol VARCHAR(255) PRIMARY KEY, " 
                "name VARCHAR(255), " 
                "current_price FLOAT, "
                "currency VARCHAR(255), "
                "product_type INT, "
                "sector INT, "
                "industry VARCHAR(255), "
                "leveraged INT, "
                "yield_5y FLOAT, "
                "yield_1y FLOAT, "
                "div_per_price FLOAT, "
                "market_cap BIGINT, "
                "profitability FLOAT, "
                "analyst_score FLOAT)" )

        except mysql.connector.errors.ProgrammingError:
            print("Table 'products' already exists")

    # should match the update def, but maybe the first def will do

  
    def is_exist(self, product):
        res = self.get_product_by_symbol( product.symbol)
        return res is not None and len(res) > 0

    def add_product(self, product):
        if isinstance(product, str):
            product = finance_product.FinanceProduct(product)
        if self.is_exist(product):
            self.update_row(product)
            return
            
        sql = "INSERT INTO products (symbol, name, type, price, yield_y5, yield_1y, dividend, pe_ratio, " \
              "profit, debt_percentage, market_cap, main_sector, borsa, avg_volume, analyst_score) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        values = product.get_brief_data_sql()
        try:
            self.mycursor.execute(sql, values)
            self.mydb.commit()
        except Exception as e:
            print("database_handler.add_product values: "+str(values))
            print(e)
        # if we want to insert several rows together mycursor.executemany(sql, values.p)

    def update_row(self, product):
        values = product.get_brief_data_sql()

        sql = "UPDATE products (name, type, price, yield_y5, yield_1y, dividend, pe_ratio, " \
            "profit, debt_percentage, market_cap, main_sector, borsa, avg_volume, analyst_score) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
            "WHERE symbol = '" + str(values[0]) + "'"
        try:
            self.mycursor.execute(sql, values[1:])
            self.mydb.commit()
        except Exception as e:
            print("database_handler.update_product values: "+str(values))
            print(e)

    def show_data(self, data):

        # todo : incase not all culumns being sent

        res = np.vstack((calculation.headlines, data))
        print(res)

    def get_all_products(self, limit=None, to_print=False):
        sql = "SELECT * FROM products"
        if limit is not None:
            sql += " LIMIT " + limit
        self.mycursor.execute(sql)
        data = self.mycursor.fetchall()
        if to_print:
            self.show_data(data)

        return data

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
        """  other options
            # select rows where the address contain "way", the "#" could be also only from one side
            # sql = "SELECT * FROM tablename WHERE address LIKE '%way%'"

            # you can limit the amount of rows selected (to 5) and starting from a certain row (2)
            # self.mycursor.execute("SELECT * FROM customers LIMIT 5 OFFSET 2")

            # mycursor.execute(sql)

            # using changing values        """

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


    def show_tables_names(self):
        self.mycursor.execute("SHOW TABLES")
        for x in self.mycursor:
            print(x)

    """     not in use any more, maybe will be in use for currency


        def add_column(self, product, column_name, col_type=""):

            self.mycursor.execute(
                "ALTER TABLE products ADD COLUMN " + column_name + col_type)


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
            return res


        # not relevante yet

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

        """

    def select_column(self, column_name, to_print):
        self.mycursor.execute("SELECT name FROM products")
        # to fetch only the first row and not all column we use mycursor.fetchone()
        myresult = self.mycursor.fetchall()

        if to_print:
            for x in myresult:
                print(x)
        
        return myresult
        """ incase of "errors.InternalError("Unread result found")" will raise
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
            #   check the manual that corresponds to your MySQL server version for the right syntax to use near... """

if __name__ == '__main__':
    print("start")
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
    db.add_product(finance_product.FinanceProduct("qld"))
    print("qld done")

    data = db.get_all_products(to_print=True)
    print("done")
 