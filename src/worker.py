from jobs import get_job_by_id, update_job_status, q, rd, rdb
import json
import logging
from datetime import datetime
import time
import redis

import logging
import socket
import os

loglevel = os.environ.get('LOG_LEVEL')
format_str=f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=loglevel, format=format_str)

@q.worker
def do_work(jobid):
    """
        Returns a frequency map of the date a gene was first approved given a gene group

        Args:
            jobid (string): specific jobid
    """
    # get job
    update_job_status(jobid, 'in progress')
    job = get_job_by_id(jobid)
    date_freq = get_trips_freq_between_dates(job['start_date'], job['end_date'])
    rdb.set(jobid, json.dumps(date_freq)) # input to results database
    update_job_status(jobid, 'complete') # update job database

def get_trips_freq_between_dates(start_date, end_date):
    """
        Returns a list of bike trips between a range of dates

        Args:
            start_date (string): starting date
            end_date (string): ending date
    """
    start = datetime.strptime(start_date, '%m/%d/%Y').date()
    end = datetime.strptime(end_date, '%m/%d/%Y').date()
    logging.debug(start, end)
    result = {}
    for key in rd.keys():
        trip = json.loads(rd.get(key))
        if trip.get('Checkout Datetime'): # none value handling
            checkout_date = trip.get('Checkout Datetime')[:10]
            date = datetime.strptime(checkout_date, '%m/%d/%Y').date()
            if date >= start and date <= end:
                result[checkout_date] = result.get(checkout_date, 0) + 1
    logging.debug(f'length of result: {len(result)}')
    if not result:
        logging.error('job did not find anything, empty result')
    return result

print(rd.info())
while rd.info()['loading'] == 1:
    time.sleep(5)

do_work()

