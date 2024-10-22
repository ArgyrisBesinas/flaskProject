import utility.job_management as job_management
import utility.jupyter_utils as jupyter_utils
import utility.snippet_management as snippet_management
import utility.custom_exceptions as exc
import synthesis.synthesize as synthesize
from flask import render_template, request


def define_routes(app):
    # @app.route('/')
    # def home():
    #     return render_template('home.html')

    @app.route('/')
    def new_job():
        # print(list(synthesize.get_synth_methods_dict().keys()))
        return render_template('new_job.html',
                               synth_methods=list(synthesize.get_synth_methods_dict().keys()),
                               licences=snippet_management.get_licence_types())

    @app.route('/list_jobs')
    def list_job():
        return render_template('list_jobs.html')

    @app.get('/job_details/<job_id>')
    def job_details(job_id):
        if job_id == 'latest':
            job_id = job_management.get_latest_job_id()
        else:
            try:
                job_id = int(job_id)
            except ValueError:
                return 'job_id must be int or "latest"', 400

        return render_template('job_details.html', job_id=job_id)

    @app.route('/manage_repos')
    def manage_repos():
        return render_template('manage_repos.html')

    @app.route('/repo_details/<source_id>')
    def repo_details(source_id):
        try:
            source_id = int(source_id)
        except ValueError:
            return 'source_id must be int', 400
        return render_template('repo_details.html',  source_id=source_id)

    @app.route('/advanced_search')
    def advanced_search():
        return render_template('advanced_search.html')

    @app.route('/import_repos')
    def import_repos():
        return render_template('import_repos.html', licences=snippet_management.get_licence_types())

    # ---------------------------------------------------
    # start of backend routes
    # ---------------------------------------------------

    # init code synth and add job to db
    @app.route('/create_new_job', methods=['POST'])
    def create_new_job():

        synth_source = request.form.get('synth_source', None, str)
        synth_method = request.args.get('synth_method', None, str)
        synth_licence = request.args.get('licence', None, str)

        if synth_source is None or synth_source == '':
            return 'synth_source is missing', 400

        if synth_method is None or synth_method == '':
            return 'synth_method is missing', 400

        if synth_licence is None or synth_licence == '':
            return 'licence is missing', 400

        try:
            job_id = synthesize.initiate_synth(synth_source, synth_method, synth_licence)

        except (exc.MySqlError, exc.SynthesisError) as e:
            return str(e), 400

        return str(job_id)

    # Get jobs in json for listing
    @app.route('/get_jobs', methods=['GET'])
    def get_jobs():

        try:
            jobs = job_management.get_jobs((), None, 'json')
        except exc.MySqlError as e:
            return str(e), 400

        return jobs, 200

    # Cancel job by job_id
    @app.route('/cancel_job', methods=['POST'])
    def cancel_job():

        job_id = request.form.get('job_id', None, int)
        if job_id is None:
            return 'job_id is required and must be int', 400

        try:
            synthesize.cancel_synth_progress([job_id], 'Canceled by user.')
        except (exc.MySqlError, exc.SynthesisError) as e:
            return str(e), 400

        return 'Job with id "' + str(job_id) + '" cancelled.', 200

    # Delete jobs by job_id
    @app.route('/delete_jobs', methods=['POST'])
    def delete_job():

        job_ids = request.form.to_dict(flat=False).get('job_ids')
        if job_ids is None or len(job_ids) == 0:
            return 'job_ids not found', 400

        try:
            rows = synthesize.cancel_synth_progress(job_ids, None, True)
        except (exc.MySqlError, exc.SynthesisError) as e:
            return str(e), 400
        else:
            if len(job_ids) > rows:
                return str(rows) + ' out of ' + str(len(job_ids)) + ' jobs deleted', 200
            else:
                return str(rows) + ' jobs deleted', 200

    # Get job details by job_id
    @app.route('/get_job_details', methods=['GET'])
    def get_job_details():

        job_id = request.args.get('job_id', None, int)
        if job_id is None:
            return 'job_id is required and must be int', 400

        try:
            job_details_data = job_management.get_job_details_by_id(job_id, None, 'json')
        except exc.MySqlError as e:
            return str(e), 400

        return job_details_data, 200

    @app.get('/test')
    def test():

        # return str(job_management.insert_job_output(10, '''aaaaaa aaaaaaa aaaaaaaa''', 3, 4)), 200

        return job_management.delete_job_outputs([10]), 200

        # return snippet_management.search_snippets(None, 'blob', 0, None, 'json'), 200

    # import snippet from url sources
    @app.route('/import_snippets_url', methods=['GET', 'POST'])
    def import_snippets_url():

        if request.method == 'GET':
            name = request.args.get('name')
            url = request.args.get('url')
            source = request.args.get('source')
            licence = request.args.get('licence')

        elif request.method == 'POST':
            name = request.form.get('name')
            url = request.form.get('url')
            source = request.form.get('source')
            licence = request.form.get('licence')

        if name is None:
            name = ''

        if licence is None:
            return "licence is required", 400

        user = '1'

        if source != 'github' and source != 'raw':
            return "source can only be 'github' or 'raw'", 400

        try:
            if source == 'github':
                snippets, python_ver = jupyter_utils.process_jupyter_json_from_github(url)
            elif source == 'raw':
                snippets, python_ver = jupyter_utils.process_jupyter_json_from_url_raw(url)
        except (exc.GetRequestError, exc.JsonDecodeError, exc.InvalidJupyterNotebookError, exc.RequestFailedError) as e:
            return str(e), 400

        try:
            rows = snippet_management.insert_new_snippets(snippets, name, url, user, False, python_ver, licence)
        except exc.MySqlError as e:
            return str(e), 400
        else:
            return str(rows) + ' snippets inserted', 200

    # import snippet from text sources
    @app.route('/import_snippets_text', methods=['POST'])
    def import_snippets_text():

        name = request.args.get('name')
        if name is None:
            name = ''

        licence = request.args.get('licence')
        if licence is None:
            return "licence is required", 400

        json = request.get_json()
        if json is None:
            return "invalid json posted", 400

        user = '1'

        try:
            snippets, python_ver = jupyter_utils.extract_snippets_from_jupyter_json(json)
        except exc.InvalidJupyterNotebookError as e:
            return str(e), 400

        try:
            rows = snippet_management.insert_new_snippets(snippets, name, None, user, True, python_ver, licence)
        except exc.MySqlError as e:
            return str(e), 400
        else:
            return str(rows) + ' snippets inserted', 200

    # delete snippet sources
    @app.route('/delete_snippet_sources', methods=['POST'])
    def delete_snippet_sources():

        snippet_source_ids = request.form.to_dict(flat=False).get('snippet_source_ids')
        if snippet_source_ids is None or len(snippet_source_ids) == 0:
            return 'snippet_source_ids not found', 400

        user = '1'

        try:
            rows = snippet_management.delete_snippet_sources(snippet_source_ids, user)
        except exc.MySqlError as e:
            return str(e), 400
        else:
            if len(snippet_source_ids) > rows:
                return str(rows) + ' out of ' + str(len(snippet_source_ids)) + ' snippet sources deleted', 200
            else:
                return str(rows) + ' snippet sources deleted', 200

    # update snippet source
    @app.route('/update_snippet_sources', methods=['POST'])
    def update_snippet_sources():

        snippet_source_ids = request.form.to_dict(flat=False).get('snippet_source_ids')
        if snippet_source_ids is None or len(snippet_source_ids) == 0:
            return 'snippet_source_ids not found', 400

        user = '1'

        try:
            snippet_sources = snippet_management.get_snippet_sources(snippet_source_ids, user)
        except exc.MySqlError as e:
            return str(e), 400

        if len(snippet_sources) == 0:
            return 'No specified snippet sources found', 400
        elif len(snippet_sources[0]) != 5:
            return 'Snippet sources malformed', 400

        snippet_sources_updated = 0
        snippets_updated = 0

        for snippet_source in snippet_sources:
            if snippet_source[1] is None or 'http' not in snippet_source[1]:
                continue

            try:
                snippets = jupyter_utils.process_jupyter_json_from_github(snippet_source[1])
            except (exc.GetRequestError, exc.JsonDecodeError, exc.InvalidJupyterNotebookError) as e:
                # return str(e), 400
                continue

            try:
                rows = snippet_management.update_snippets(snippet_source[0], snippets, snippet_source[1], user)
            except exc.MySqlError as e:
                # return str(e), 400
                continue
            else:
                snippet_sources_updated += 1
                snippets_updated += rows

        return str(snippet_sources_updated) + ' snippet source(s) updated and ' + str(
            snippets_updated) + ' snippets updated', 200

    # get snippet source
    @app.route('/get_snippet_sources', methods=['GET'])
    def get_snippet_sources():

        snippet_source_id_args = ()

        snippet_source_ids = request.args.getlist('snippet_source_id')
        if snippet_source_ids is not None and len(snippet_source_ids) > 0:
            snippet_source_id_args = snippet_source_ids

        try:
            sources = snippet_management.get_snippet_sources(snippet_source_id_args, None, None, 'json')
        except exc.MySqlError as e:
            return str(e), 400

        return sources, 200

    # toggle snippet source
    @app.route('/toggle_snippet_sources', methods=['POST'])
    def disable_snippet_sources():

        snippet_source_ids = request.form.to_dict(flat=False).get('snippet_source_ids')
        if snippet_source_ids is None or len(snippet_source_ids) == 0:
            return 'snippet_source_ids not found', 400

        set_value = request.form.get('set_value')
        if set_value is None:
            return 'set_value not found', 400
        elif set_value == '0':
            toggle_action = 'enabled'
        elif set_value == '1':
            toggle_action = 'disabled'
        else:
            return 'set_value must be "0" or "1"', 400

        try:
            rows = snippet_management.toggle_snippet_sources(snippet_source_ids, set_value)
        except exc.MySqlError as e:
            return str(e), 400
        else:
            if len(snippet_source_ids) > rows:
                return str(rows) + ' out of ' + str(len(snippet_source_ids)) + ' snippet sources ' + toggle_action, 200
            else:
                return str(rows) + ' snippet sources ' + toggle_action, 200

    # get snippet from source
    @app.route('/get_snippets_from_source', methods=['GET'])
    def get_snippets_from_source():

        snippet_source_ids = request.args.getlist('snippet_source_id')
        if snippet_source_ids is None or len(snippet_source_ids) == 0:
            return 'snippet_source_id not found', 400

        try:
            snippets = snippet_management.get_snippets_from_sources(snippet_source_ids, None, 'json')
        except exc.MySqlError as e:
            return str(e), 400

        return snippets, 200

    # toggle snippets
    @app.route('/toggle_snippets', methods=['POST'])
    def toggle_snippets():

        snippet_source_id = request.form.get('snippet_source_id')
        if snippet_source_id is None:
            return 'snippet_source_id not found', 400

        snippet_local_ids = request.form.to_dict(flat=False).get('snippet_local_ids')
        if snippet_local_ids is None or len(snippet_local_ids) == 0:
            return 'snippet_local_ids not found', 400

        set_value = request.form.get('set_value')
        if set_value is None:
            return 'set_value not found', 400
        elif set_value == '0':
            toggle_action = 'enabled'
        elif set_value == '1':
            toggle_action = 'disabled'
        else:
            return 'set_value must be "0" or "1"', 400

        try:
            rows = snippet_management.toggle_snippets(snippet_source_id, snippet_local_ids, set_value)
        except exc.MySqlError as e:
            return str(e), 400
        else:
            if len(snippet_local_ids) > rows:
                return str(rows) + ' out of ' + str(
                    len(snippet_local_ids)) + ' snippets ' + toggle_action, 200
            else:
                return str(rows) + ' snippets ' + toggle_action, 200

    # search snippets
    @app.route('/search_snippets', methods=['POST'])
    def search_snippets():

        description_search_text = request.form.get('description_search_text', None, str)
        code_search_text = request.form.get('code_search_text', None, str)
        include_disabled = request.form.get('include_disabled', None, int)
        licence = request.form.get('licence', None, int)

        try:
            snippets = snippet_management.search_snippets(description_search_text, code_search_text, include_disabled,
                                                          None, licence, 'json')
        except exc.MySqlError as e:
            return str(e), 400

        return snippets, 200
