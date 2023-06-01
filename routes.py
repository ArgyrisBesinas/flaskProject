import utility.job_management as job_management
from flask import render_template


def define_routes(app):
    @app.route('/')
    def hello_world():
        return render_template('home.html')

    @app.route('/new_job')
    def new_job():
        return render_template('home.html')

    @app.route('/repos')
    def repos():
        return render_template('home.html')

    @app.get('/recent_jobs')
    def recent_jobs():
        return render_template('child.html')

    @app.get('/job_info/')
    @app.get('/job_info/<uuid>')
    def job_info(uuid=None):
        if uuid == '123':
            return 'Job Info!'
        else:
            return render_template('404.html')

    @app.get('/create_new_job')
    def create_new_job():
        return job_management.insert_new_job_and_return_id()

    @app.get('/test')
    def test():
        return job_management.get_jobs_info_by_id(('26274df8-5b52-4d85-b85f-552683515882', 'aaa'))



