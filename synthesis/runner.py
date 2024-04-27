import utility.job_management as job_management
from datetime import datetime

"""
class Snippet:
    pass


class AbstractSynthesizer:
    def __init__(self, job_id):
        self.job_id = job_id

    def add_line(self, snippet):
        job_management.insert_job_output(self.job_id, snippet.text, snippet.src1, snipper.src2)


class BWSyntesize(AbstractSynthesizer):
    def synthesize(self):
        self.add_line(snippet)
"""


def start_synthesis(job_id, text):
    # details = job_management.get_job_details_by_id(job_id)

    # snippet_management.search_snippets(None, 'blob', 0)

    timestamp_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    job_management.edit_job_by_id(job_id, "Running", info="Searching", progress_percent=0)
    job_management.edit_job_by_id(job_id, "Running", info="Fitting", progress_percent=50)

    job_management.insert_job_output(job_id, "test", 3, 1)

    job_management.edit_job_by_id(job_id, "Running", progress_percent=100)
    job_management.edit_job_by_id(job_id, 'Completed', None, None, None, timestamp_end)

    # delete_job_outputs
    # job_management.delete_job_outputs([job_id])
