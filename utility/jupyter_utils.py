import requests
import utility.custom_exceptions as exc


# returns snippets list
def process_jupyter_json_from_github(url):
    # github urls are case-sensitive
    # url = url.lower()
    if 'https://github.com/' not in url or '/blob/' not in url:
        return "Not valid github url"

    url = url.replace('https://github.com/', 'https://raw.githubusercontent.com/')
    url = url.replace('/blob/', '/')

    return process_jupyter_json_from_url_raw(url)


def process_jupyter_json_from_url_raw(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise exc.RequestFailedError('Get request failed for url: ' + url)

    if not r.ok:
        raise exc.GetRequestError('Response code not 200')

    try:
        json = r.json()
    except requests.exceptions.JSONDecodeError as e:
        raise exc.JsonDecodeError('Json decode error')
    return extract_snippets_from_jupyter_json(json)


def validate_jupyter_json(json, strict=False):
    err = []
    if 'cells' not in json:
        err.append('cells')

    if strict:
        if 'metadata' not in json:
            err.append('metadata')
        if 'nbformat' not in json:
            err.append('nbformat')
        if 'nbformat_minor' not in json:
            err.append('nbformat_minor')

    if len(err) > 0:
        raise exc.InvalidJupyterNotebookError('Json missing following keys: ' + ', '.join(err))


def validate_jupyter_cell(cell):
    if 'cell_type' not in cell or 'source' not in cell:
        return False
    return True


def extract_snippets_from_jupyter_json(json):
    validate_jupyter_json(json)

    python_ver = None
    if json.get('metadata').get('language_info').get('name') == 'python' and \
            json.get('metadata').get('language_info').get('version') is not None:
        python_ver = json.get('metadata').get('language_info').get('version')

    snippets = []
    local_id = 0
    cells = json.get('cells')

    for i, c in enumerate(cells):
        if not validate_jupyter_cell(c):
            continue
        if c.get('cell_type') != 'code':
            continue
        if cells[i-1].get('cell_type') == 'markdown':
            snippet = {
                'local_id': local_id,
                'parent_id': None,
                'desc': ' '.join(cells[i-1].get('source')),
                'code': ' '.join(c.get('source'))
            }
        else:
            snippet = {
                'local_id': local_id,
                'parent_id': None,
                'desc': '',
                'code': ' '.join(c.get('source'))
            }
        local_id += 1
        snippets.append(snippet)

    return snippets, python_ver
