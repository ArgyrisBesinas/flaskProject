from utility.database import get_mysql_connection
import mysql.connector.errors as db_errors
import utility.custom_exceptions as exc
import json


def insert_new_job_and_return_id(synth_source, user=1):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = ("INSERT INTO jobs "
           "(`status`, `synth_source`, `user`) "
           "VALUES (%s, %s, %s)")

    try:
        cursor.execute(sql, ('starting', synth_source, user))
    except db_errors.Error as err:
        print('insert_new_job_and_return_id error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error inserting new job.')
    else:
        mysql_connection.commit()

    job_id = cursor.lastrowid

    cursor.close()

    return job_id


# if optional args are 'None' they will be ignored and not overwritten
def edit_job_by_id(job_id: int, status, info=None, progress_percent: int = None, date_end=None,
                   user=1):
    if job_id is None:
        raise exc.MySqlError('"job_id" required to edit job.')
    elif status is None:
        raise exc.MySqlError('"status" required to edit job.')

    sql_fields_string = 'status=%s, user=%s'
    sql_values = [status, user]

    if info is not None:
        sql_fields_string = sql_fields_string + ', info=%s'
        sql_values.append(info)

    if progress_percent is not None:
        sql_fields_string = sql_fields_string + ', progress_percent=%s'
        sql_values.append(progress_percent)

    if date_end is not None:
        sql_fields_string = sql_fields_string + ', date_end=%s'
        sql_values.append(date_end)

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = 'UPDATE jobs SET ' + sql_fields_string + ' WHERE job_id=%s'

    try:
        cursor.execute(sql, (*sql_values, job_id))
    except db_errors.Error as err:
        print('edit_job_by_id error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error editing job with id: ' + str(job_id))
    else:
        mysql_connection.commit()

    cursor.close()

    return


def get_jobs(job_ids=(), user=None, data_type=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = 'SELECT * FROM jobs'
    if job_ids is not None and len(job_ids) > 0:
        sql = sql + 'WHERE `job_id`IN (' + ', '.join(['%s'] * len(job_ids)) + ')'
        if user is not None:
            sql += ' AND user = ' + user
    elif user is not None:
        sql += ' WHERE user = ' + user

    try:
        cursor.execute(sql, job_ids)
    except db_errors.Error as err:
        print('get_jobs error.', err)
        raise exc.MySqlError('Error getting jobs')

    data = cursor.fetchall()

    if data_type == 'json':
        row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        json_data = []
        for row in data:
            json_data.append(dict(zip(row_headers, row)))

        data = json.dumps(json_data, default=str)

    cursor.close()

    return data


def delete_jobs(job_ids, user=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''DELETE FROM jobs 
                    WHERE `job_id`IN (''' + ', '.join(['%s'] * len(job_ids)) + ')'
    if user is not None:
        sql += "AND user = " + user

    try:
        cursor.execute(sql, job_ids)
    except db_errors.Error as err:
        print('delete_jobs error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error deleting jobs')
    else:
        print(cursor.rowcount, "jobs deleted.")
        mysql_connection.commit()

    jobs_deleted = cursor.rowcount

    cursor.close()

    return jobs_deleted


def get_job_details_by_id(job_id, user=None, data_type=None):
    if data_type is not None and data_type != 'json':
        raise exc.MySqlError('Error getting job details sources. "data_type" must be json or None')

    if job_id is None:
        raise exc.MySqlError('job_id required to get job details.')

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = 'SELECT * FROM jobs WHERE `job_id`=%s'
    if user is not None:
        sql += ' AND user = ' + user

    try:
        cursor.execute(sql, (job_id,))
    except db_errors.Error as err:
        print('get_jobs_details_by_id get job error.', err)
        raise exc.MySqlError('Error getting job details')

    data = cursor.fetchall()

    if len(data) == 0:
        print('job with id ' + str(job_id) + ' not found.')
        raise exc.MySqlError('job with id ' + str(job_id) + ' not found.')
    elif len(data) > 1:
        print('multiple jobs with id ' + str(job_id) + ' found.')
        raise exc.MySqlError('multiple jobs with id ' + str(job_id) + ' found.')

    row_headers = [x[0] for x in cursor.description]
    json_data = dict(zip(row_headers, data[0]))

    cursor.close()

    cursor = mysql_connection.cursor()

    sql = 'SELECT * FROM job_output WHERE `job_id`=%s ORDER BY job_id DESC'

    try:
        cursor.execute(sql, (job_id,))
    except db_errors.Error as err:
        print('get_jobs_details_by_id get job outputs error.', err)
        raise exc.MySqlError('Error getting job details')

    data = cursor.fetchall()

    print(json_data)

    row_headers = [x[0] for x in cursor.description]
    json_data['job_outputs'] = []
    for row in data:
        json_data['job_outputs'].append(dict(zip(row_headers, row)))

    if data_type == 'json':
        json_data = json.dumps(json_data, default=str)

    return json_data


def insert_job_output(job_id: int, code_output, snippet_source_id, snippet_local_id):
    if job_id is None or code_output is None or snippet_source_id is None or snippet_local_id is None:
        raise exc.MySqlError('all arguments required to insert job output.')

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = ("INSERT INTO job_output "
           "(`job_id`, `code`, `snippet_source_id`, `snippet_local_id`) "
           "VALUES (%s, %s, %s, %s)")

    try:
        cursor.execute(sql, (job_id, code_output, snippet_source_id, snippet_local_id))
    except db_errors.Error as err:
        print('insert_job_output error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error inserting new job output.')
    else:
        mysql_connection.commit()

    cursor.close()

    return


def get_latest_job_id(user=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = 'SELECT MAX(job_id) FROM jobs'
    if user is not None:
        sql += ' WHERE user = ' + user

    try:
        cursor.execute(sql)
    except db_errors.Error as err:
        print('get_latest_job_id error.', err)
        raise exc.MySqlError('Error getting jobs')

    data = cursor.fetchall()

    cursor.close()

    return data[0][0]


def delete_job_outputs(job_ids, user=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''DELETE FROM job_output 
                    WHERE `job_id`IN (''' + ', '.join(['%s'] * len(job_ids)) + ')'
    if user is not None:
        sql += "AND user = " + user

    try:
        cursor.execute(sql, job_ids)
    except db_errors.Error as err:
        print('delete_job_outputs error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error deleting job outputs')
    else:
        print(cursor.rowcount, "job outputs deleted.")
        mysql_connection.commit()

    job_outputs_deleted = cursor.rowcount

    cursor.close()

    return job_outputs_deleted
