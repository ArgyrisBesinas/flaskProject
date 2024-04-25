import utility.job_management as job_management
import utility.custom_exceptions as exc
from datetime import datetime


def initiate_synth(synth_source):
    # 1. insert new job to db
    job_id = job_management.insert_new_job_and_return_id(synth_source)
    if job_id is None:
        raise exc.MySqlError('Error inserting new job')
    # 2. start synth in module
    # error = start_synth(text)
    error = None

    if error is not None:
        # update_snippet('error')
        raise exc.SynthesisError('Error inserting new job')

    # 3. if synth started successfully return job_id
    return job_id


# you can also use the two functions inside separately
def update_synth_progress(job_id, status, info=None, progress_steps=None, progress_percent=None, date_end=None,
                          code_output=None, snippet_source_id=None, snippet_local_id=None):
    # to update synth progress in job
    job_management.edit_job_by_id(job_id, status, info, progress_steps, progress_percent, date_end)
    # if you also simultaneously output generated code use
    if code_output is not None:
        job_management.insert_job_output(job_id, code_output, snippet_source_id, snippet_local_id)


# function called to stop synth job execution
def cancel_synth_progress(job_ids, info=None, delete=False):
    for job_id in job_ids:
        # code to stop synth execution by job_id if active
        if not delete:
            progress_steps = None
            progress_percent = None
            timestamp_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # update job in db. Parameters =None will not be overwritten to null in db
            job_management.edit_job_by_id(job_id, 'cancelled', info, progress_steps, progress_percent, timestamp_end)

    if delete:
        return job_management.delete_jobs(job_ids)
