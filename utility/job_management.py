from utility.database import get_mysql_connection
from datetime import datetime
from uuid import uuid4


def insert_new_job_and_return_id():
    job_id = str(uuid4())

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()
    # cursor.execute("USE {}".format(os.environ['MYSQL_DB_NAME']))

    sql = ("INSERT INTO jobs "
               "(`uuid`,`status`,`date`) "
               "VALUES (%s, %s, %s)")

    data_job = (job_id, 'pending', str(datetime.now()))

    try:
        cursor.execute(sql, data_job)
    except mysql_connection.connector.Error as err:
        print('insert_new_job_and_return_id error.', err)
    else:
        mysql_connection.commit()

    cursor.close()

    return job_id


def get_jobs_info_by_id(uuids):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''SELECT * FROM jobs 
               WHERE `uuid`IN (''' + ', '.join(['%s'] * len(uuids)) + ')'

    try:
        cursor.execute(sql, uuids)
    except mysql_connection.connector.Error as err:
        print('get_jobs_info_by_id error.', err)
    else:
        result = cursor.fetchall()
        print(result[0][1])

    cursor.close()

    return ""
