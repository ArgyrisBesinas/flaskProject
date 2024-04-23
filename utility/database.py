import os
import mysql.connector
from mysql.connector import errorcode


def get_mysql_connection():

    try:
        db_connection = mysql.connector.connect(
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASSWORD'],
            host=os.environ['MYSQL_URL'],
            database=os.environ['MYSQL_DB_NAME']
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

        exit(1)
    else:
        return db_connection


def init_db():

    try:
        mysql_connection = mysql.connector.connect(
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASSWORD'],
            host=os.environ['MYSQL_URL']
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        else:
            print(err)
        exit(1)

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
    tables['jobs'] = (
        "CREATE TABLE `jobs` ("
        "  `job_nr` int(11) NOT NULL UNIQUE AUTO_INCREMENT,"
        "  `uuid` varchar(50) NOT NULL,"
        "  `status` varchar(50) NOT NULL,"
        "  `date` datetime NOT NULL,"
        "  PRIMARY KEY (`job_nr`)"
        ") ENGINE=InnoDB")

    tables['snippet_sources'] = (
        "CREATE TABLE `snippet_sources` ("
        "  `snippet_source_id` int(11) NOT NULL UNIQUE AUTO_INCREMENT,"
        "  `name` varchar(500),"
        "  `url` varchar(500) UNIQUE,"
        "  `manual_entry` boolean NOT NULL DEFAULT false,"
        "  `python_ver` varchar(50),"
        "  `user` int(11) NOT NULL,"
        "  `last_updated` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
        "  `disabled` boolean NOT NULL DEFAULT 0,"
        "  PRIMARY KEY (`snippet_source_id`)"
        ") ENGINE=InnoDB")

    tables['snippets'] = (
        "CREATE TABLE `snippets` ("
        "  `snippet_source_id` int(11) NOT NULL,"
        "  `snippet_local_id` int(11) NOT NULL,"
        "  `parent_id` int(11),"
        "  `description` text NOT NULL,"
        "  `code` text NOT NULL,"
        "  `disabled` boolean NOT NULL DEFAULT 0,"
        "  PRIMARY KEY (`snippet_source_id`, `snippet_local_id`),"
        "  FOREIGN KEY (snippet_source_id)"
        "     REFERENCES snippet_sources (snippet_source_id)"
        "     ON DELETE CASCADE"
        ") ENGINE=InnoDB")

    tables['users'] = (
        "CREATE TABLE `users` ("
        "  `user_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `username` varchar(255) NOT NULL UNIQUE,"
        "  `password` varchar(255) NOT NULL,"
        "  `email` varchar(255) NOT NULL UNIQUE ,"
        "  PRIMARY KEY (`user_id`)"
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

    cursor.close()


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(os.environ['MYSQL_DB_NAME']))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

