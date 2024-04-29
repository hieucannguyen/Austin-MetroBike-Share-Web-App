from jobs import get_job_by_id, update_job_status, q, rd, rdb
import json
import logging
from datetime import datetime
import time
from matplotlib import pyplot as plt

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
    create_chart(date_freq)
    with open('/bike_trips_chart.png', 'rb') as f:
        img = f.read()
    rdb.hset(jobid, 'image', img) # input to results database
    update_job_status(jobid, 'complete') # update job database

def get_trips_freq_between_dates(start_date, end_date):
    """
        Returns a list of bike trips between a range of dates

        Args:
            start_date (datetime): starting date
            end_date (datetime): ending date
    """
    logging.debug(start_date, end_date)
    group_by_days = True
    if (start_date - end_date).days > 100:
        group_by_days = False
    result = {}
    for key in rd.keys():
        trip = json.loads(rd.get(key))
        if trip.get('Checkout Datetime'): # none value handling
            checkout_date = trip.get('Checkout Datetime')[:10]
            checkout_date_by_month = checkout_date[:2]+'/'+checkout_date[6:10]
            date = datetime.strptime(checkout_date, '%m/%d/%Y').date()
            if date >= start_date and date <= end_date:
                if group_by_days:
                    result[checkout_date] = result.get(checkout_date, 0) + 1
                else:
                    result[checkout_date_by_month] = result.get(checkout_date_by_month, 0) + 1
    logging.debug(f'length of result: {len(result)}')
    if not result:
        logging.error('job did not find anything, empty result')
    return result

def create_chart(result):
    """
        Returns a bar chart with dates and number of bike trips

        Args:
            result (dict): dictionary of dates and counts
    """
    sorted_result = dict(sorted(result.items()))
    plt.bar(list(sorted_result.keys()), sorted_result.values())
    plt.xlabel('Date')
    plt.xticks(rotation=90)
    plt.ylabel('Number of Trips')
    plt.savefig('bike_trips_chart.png')


while rd.info()['loading'] == 1: # ensure redis is not loading
    time.sleep(5)

do_work()

