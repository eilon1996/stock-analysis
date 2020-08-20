import mysql.connector


def create_new_data_base():
    mydb = mysql.connector.connect(
        host="localhost",
        user="eilon",
        password="12qwaszx",
        database="test"
    )

    mycursor = mydb.cursor()
    mycursor.execute("USE test")
    # neceserry only for the first time
    return mydb, mycursor


def aaa(mydb):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE test")
        mycursor.execute("USE test")

    except mysql.connector.errors.DatabaseError:
        # in case database is already exist
        mydb = mysql.connector.connect(
            host="localhost",
            user="eilon",
            password="12QWaszx",
            database="mydatabase")
    mycursor = mydb.cursor()

create_new_data_base()

print("done")