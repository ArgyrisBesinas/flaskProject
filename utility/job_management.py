from utility.database import get_mysql_connection
from datetime import datetime
from uuid import uuid4


def insert_new_job_and_return_id():
    job_id = str(uuid4())

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()
    # cursor.execute("USE {}".format(os.environ['MYSQL_DB_NAME']))

    add_job = ("INSERT INTO jobs "
               "(`uuid`,`status`,`date`) "
               "VALUES (%s, %s, %s)")

    data_job = (job_id, 'pending', str(datetime.now()))

    cursor.execute(add_job, data_job)

    mysql_connection.commit()
    cursor.close()

    return job_id


def get_jobs_info_by_id(uuids):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    get_jobs = '''SELECT * FROM jobs 
               WHERE `uuid`IN (''' + ', '.join(['%s'] * len(uuids)) + ')'



    cursor.execute(get_jobs, uuids)

    result = cursor.fetchall()
    print(result[0][1])

    cursor.close()

    return ""
