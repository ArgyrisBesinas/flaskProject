import os
import mysql.connector
from mysql.connector import errorcode


def get_mysql_connection():

    try:
        db_connection = mysql.connector.connect(
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASSWORD'],
            host=os.environ['MYSQL_URL']
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        else:
            print(err)

        return None, err
    else:
        return db_connection, None
        db_connection.close()

    return None, 'get_mysql_connection error'


def init_db():
    mysql_connection, err = get_mysql_connection()
    if err:
        print('initDB error')
        return 'initDB error'

    cursor = mysql_connection.cursor()

    db_name = os.environ['MYSQL_DB_NAME']

    try:
        cursor.execute("USE {}".format(db_name))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(db_name))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(db_name))
            mysql_connection.database = db_name
        else:
            print(err)
            exit(1)

    tables = {}
    tables['employees'] = (
        "CREATE TABLE `jobs` ("
        "  `job_nr` int(11) NOT NULL AUTO_INCREMENT,"
        "  `uuid` varchar(50) NOT NULL,"
        "  `status` varchar(50) NOT NULL,"
        "  `date` date NOT NULL,"
        "  PRIMARY KEY (`job_nr`)"
        ") ENGINE=InnoDB")

    for table_name in tables:
        table_description = tables[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    print(mysql_connection)


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(os.environ['MYSQL_DB_NAME']))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

