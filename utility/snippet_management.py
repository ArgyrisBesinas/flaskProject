from utility.database import get_mysql_connection
import utility.custom_exceptions as exc
import mysql.connector.errors as db_errors
import json
import synthesis.preprocess as preprocess


def insert_new_snippets(snippets, name, url, user, manual=False, python_ver=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = "INSERT INTO snippet_sources (name, url, user, manual_entry, python_ver) VALUES (%s, %s, %s, %s, %s)"

    try:
        cursor.execute(sql, (name, url, user, manual, python_ver))
    except db_errors.Error as err:
        print('snippet_source error.', err)
        mysql_connection.rollback()
        if 'Duplicate entry' in err.msg:
            raise exc.MySqlError('Error inserting new snippet_source. Duplicate entry.')
        else:
            raise exc.MySqlError('Error inserting new snippet_source.')
    else:
        print(cursor.rowcount, "snippet_source inserted.")

    snippet_source_id = cursor.lastrowid

    data = []
    for snippet in snippets:
        data.append(
            (
                snippet_source_id,
                snippet.get('local_id'),
                snippet.get('parent_id'),
                preprocess.preprocess_snippet_desc(snippet.get('desc')),
                snippet.get('code'),
            )
        )

    sql = "INSERT INTO snippets (snippet_source_id, snippet_local_id, parent_id, description, code) " \
          "VALUES (%s, %s, %s, %s, %s)"

    try:
        cursor.executemany(sql, data)
    except db_errors.Error as err:
        print('insert_new_snippets error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error inserting new snippets')
    else:
        print(cursor.rowcount, "snippets inserted.")
        mysql_connection.commit()

    snippets_inserted = cursor.rowcount
    cursor.close()

    return snippets_inserted


def delete_snippet_sources(snippet_source_ids, user=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''DELETE FROM snippet_sources 
                WHERE `snippet_source_id`IN (''' + ', '.join(['%s'] * len(snippet_source_ids)) + ')'
    if user is not None:
        sql += "AND user = " + user

    try:
        cursor.execute(sql, snippet_source_ids)
    except db_errors.Error as err:
        print('delete_snippet_sources error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error deleting snippet sources')
    else:
        print(cursor.rowcount, "snippet sources deleted.")
        mysql_connection.commit()

    sources_deleted = cursor.rowcount

    cursor.close()

    return sources_deleted


def update_snippets(snippet_source_id, name, snippets, url, user=None, python_ver=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = "DELETE FROM snippet_sources WHERE `snippet_source_id` = '%s' AND `manual_entry`=False"
    if user is not None:
        sql += " AND user = " + user

    try:
        cursor.execute(sql, [snippet_source_id])
    except db_errors.Error as err:
        print('delete_snippet_sources error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error deleting snippet sources')
    else:
        print(cursor.rowcount, "snippet sources deleted.")

    sql = "INSERT INTO snippet_sources (snippet_source_id, name, url, user, manual_entry, python_ver) " \
          "VALUES (%s, %s, %s, %s, %s, %s)"

    try:
        cursor.execute(sql, (snippet_source_id, name, url, user, False, python_ver))
    except db_errors.Error as err:
        print('snippet_source error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error inserting new snippet_source')
    else:
        print(cursor.rowcount, "snippet_source inserted.")

    snippet_source_id = cursor.lastrowid

    data = []
    for snippet in snippets:
        data.append(
            (
                snippet_source_id,
                snippet.get('local_id'),
                snippet.get('parent_id'),
                preprocess.preprocess_snippet_desc(snippet.get('desc')),
                snippet.get('code'),
            )
        )

    sql = "INSERT INTO snippets (snippet_source_id, snippet_local_id, parent_id, description, code) " \
          "VALUES (%s, %s, %s, %s, %s)"

    try:
        cursor.executemany(sql, data)
    except db_errors.Error as err:
        print('insert_new_snippets error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error inserting new snippets')
    else:
        print(cursor.rowcount, "snippets inserted.")
        mysql_connection.commit()

    snippets_inserted = cursor.rowcount
    cursor.close()

    return snippets_inserted


def get_snippet_sources(snippet_source_ids=(), user=None, data_type=None):
    if data_type is not None and data_type != 'json':
        raise exc.MySqlError('Error getting snippet sources. "data_type" must be json or None')

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = 'SELECT * FROM snippet_sources'

    if snippet_source_ids is not None and len(snippet_source_ids) > 0:
        sql += ' WHERE `snippet_source_id` IN (' + ', '.join(['%s'] * len(snippet_source_ids)) + ')'
        if user is not None:
            sql += ' AND user = ' + user
    elif user is not None:
        sql += ' WHERE user = ' + user

    try:
        cursor.execute(sql, snippet_source_ids)
    except db_errors.Error as err:
        print('get_snippet_sources error.', err)
        raise exc.MySqlError('Error getting snippet sources')

    data = cursor.fetchall()

    if data_type == 'json':
        row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        json_data = []
        for row in data:
            json_data.append(dict(zip(row_headers, row)))

        data = json.dumps(json_data, default=str)

    cursor.close()

    return data


def toggle_snippet_sources(snippet_source_ids, set_value, user=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''UPDATE snippet_sources 
             SET disabled = %s
             WHERE `snippet_source_id`IN (''' + ', '.join(['%s'] * len(snippet_source_ids)) + ')'
    if user is not None:
        sql += "AND user = " + user

    try:
        cursor.execute(sql, (set_value, *snippet_source_ids))
    except db_errors.Error as err:
        print('toggle_snippet_sources error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error toggling snippet sources')
    else:
        print(cursor.rowcount, "snippet sources toggled.")
        mysql_connection.commit()

    sources_disabled = cursor.rowcount

    cursor.close()

    return sources_disabled


def get_snippets_from_sources(snippet_source_ids=(), user=None, data_type=None):
    if data_type is not None and data_type != 'json':
        raise exc.MySqlError('Error getting snippets. "data_type" must be json or None')

    if snippet_source_ids is None or len(snippet_source_ids) == 0:
        raise exc.MySqlError('Error getting snippets. At least 1 "snippet_source_id" is needed')

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = 'SELECT * FROM snippets WHERE `snippet_source_id` IN (' + ', '.join(['%s'] * len(snippet_source_ids)) + ')'

    if user is not None:
        sql += ' AND user = ' + user

    print(sql)

    try:
        cursor.execute(sql, snippet_source_ids)
    except db_errors.Error as err:
        print('get_snippets_from_sources error.', err)
        raise exc.MySqlError('Error getting snippets')

    data = cursor.fetchall()

    if data_type == 'json':
        row_headers = [x[0] for x in cursor.description]
        json_data = []
        for row in data:
            json_data.append(dict(zip(row_headers, row)))

        data = json.dumps(json_data, default=str)

    cursor.close()

    return data


def toggle_snippets(snippet_source_id, snippet_local_ids, set_value, user=None):
    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''UPDATE snippets 
                SET disabled = %s
                WHERE `snippet_source_id` = %s 
                AND `snippet_local_id` IN (''' + ', '.join(['%s'] * len(snippet_local_ids)) + ')'
    if user is not None:
        sql += "AND user = " + user

    try:
        cursor.execute(sql, (set_value, snippet_source_id, *snippet_local_ids))
    except db_errors.Error as err:
        print('toggle_snippets error.', err)
        mysql_connection.rollback()
        raise exc.MySqlError('Error toggling snippets')
    else:
        print(cursor.rowcount, "snippets toggled.")
        mysql_connection.commit()

    sources_disabled = cursor.rowcount

    cursor.close()

    return sources_disabled


# if all args are None, returns all snippets
def search_snippets(description_search_text=None, code_search_text=None, disabled=None, user=None, data_type=None):
    if data_type is not None and data_type != 'json':
        raise exc.MySqlError('Error searching snippets. "data_type" must be json or None')

    mysql_connection = get_mysql_connection()

    cursor = mysql_connection.cursor()

    sql = '''
        SELECT 
            s.snippet_source_id, 
            s.snippet_local_id,
            ss.name,
            ss.url,
            ss.manual_entry,
            ss.last_updated,
            ss.disabled as source_disabled,
            s.description,
            s.code,
            s.disabled as snippet_disabled
        FROM snippets AS s LEFT JOIN snippet_sources ss on ss.snippet_source_id = s.snippet_source_id 
        WHERE 1=1 '''
    sql_args = []

    if description_search_text is not None:
        sql += 'AND LOWER(s.description) LIKE %s '
        sql_args.append('%' + description_search_text + '%')

    if code_search_text is not None:
        sql += 'AND LOWER(s.code) LIKE %s COLLATE '
        sql_args.append('%' + code_search_text + '%')

    if code_search_text is not None:
        sql += 'AND s.disabled = %s '
        sql_args.append(disabled)

    if user is not None:
        sql += 'AND s.user = %s'
        sql_args.append(user)

    try:
        cursor.execute(sql, sql_args)
    except db_errors.Error as err:
        print('search_snippets error.', err)
        raise exc.MySqlError('Error searching snippets')

    data = cursor.fetchall()

    row_headers = [x[0] for x in cursor.description]
    json_data = []
    for row in data:
        json_data.append(dict(zip(row_headers, row)))

    cursor.close()

    if data_type == 'json':
        return json.dumps(json_data, default=str)

    return json_data
