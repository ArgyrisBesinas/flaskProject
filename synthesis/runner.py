import utility.job_management as job_management
from datetime import datetime
import json

def start_synthesis(job_id, text):
    #details = json.loads(job_management.get_job_details_by_id(job_id))

    timestamp_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    job_management.edit_job_by_id(job_id, "Running", info="Searching", progress_percent=0)
    job_management.edit_job_by_id(job_id, "Running", info="Fitting", progress_percent=50)

    job_management.insert_job_output(job_id, "test", 3, 1)

    job_management.edit_job_by_id(job_id, "Running", progress_percent=100)
    job_management.edit_job_by_id(job_id, 'Completed', None, None, None, timestamp_end)
