import json
import uuid
import redis
from hotqueue import HotQueue

import os
import logging
import socket

redis_host = os.environ.get('REDIS_HOST')
_redis_port='6379'

rd = redis.Redis(host=redis_host, port=_redis_port, db=0, decode_responses=True) # redis database
q = HotQueue("queue", host=redis_host, port=_redis_port, db=1) # queue database
jdb = redis.Redis(host=redis_host, port=_redis_port, db=2, decode_responses=True) # job database
rdb = redis.Redis(host=redis_host, port=_redis_port, db=3) # results database

loglevel = os.environ.get('LOG_LEVEL')
format_str=f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=loglevel, format=format_str)

def _generate_jid():
    """
    Generate a pseudo-random identifier for a job.
    """
    return str(uuid.uuid4())

def _instantiate_job(jid, status, start_date, end_date):
    """
    Create the job object description as a python dictionary. Requires the job id,
    status, start_date, and end_date parameters.
    """
    logging.debug(f'jid: {jid}, status: {status}, start_date: {start_date}, end_date: {end_date}')
    return {'id': jid,
            'status': status,
            'start_date': start_date,
            'end_date': end_date}

def _save_job(jid, job_dict):
    """Save a job object in the Redis database."""
    jdb.set(jid, json.dumps(job_dict))
    logging.debug(f'jid: {jid}, job: {job_dict}')
    return

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)
    return

def add_job(start_date, end_date, status="submitted"):
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, start_date, end_date)
    _save_job(jid, job_dict)
    _queue_job(jid)
    return job_dict

def get_job_by_id(jid):
    """Return job dictionary given jid"""
    return json.loads(jdb.get(jid))

def update_job_status(jid, status):
    """Update the status of job with job id `jid` to status `status`."""
    job_dict = get_job_by_id(jid)
    if job_dict:
        job_dict['status'] = status
        _save_job(jid, job_dict)
    else:
        logging.error('Unable to update job status')
        raise Exception()
