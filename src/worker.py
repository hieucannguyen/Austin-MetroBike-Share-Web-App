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
    date_freq, group = get_trips_freq_between_dates(job['start_date'], job['end_date'])
    logging.debug(date_freq)
    create_chart(date_freq, group)
    with open('bike_trips_chart.png', 'rb') as f:
        img = f.read()
    logging.debug(type(img))
    rdb.hset(jobid, 'image', img) # input to results database
    update_job_status(jobid, 'complete') # update job database

def get_trips_freq_between_dates(start_date: str, end_date: str):
    """
        Returns a list of bike trips between a range of dates

        Args:
            start_date (datetime): starting date
            end_date (datetime): ending date
    """
    logging.debug(f'{start_date}, {end_date}')
    start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
    end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
    group_by_days = True
    if (end_date - start_date).days > 61: # ensure plot is not over crowded
        group_by_days = False
    result = {}
    for key in rd.keys():
        trip = json.loads(rd.get(key))
        if trip.get('Checkout Datetime'): # none value handling
            checkout_date = trip.get('Checkout Datetime')[:10] # mm/dd/yyyy
            checkout_date_by_month = checkout_date[:2]+'/'+checkout_date[6:10] # yyyy/mm
            date = datetime.strptime(checkout_date, '%m/%d/%Y').date()
            if date >= start_date and date <= end_date:
                if group_by_days:
                    result[checkout_date] = result.get(checkout_date, 0) + 1 # reverse so it sorts properly
                else:
                    result[checkout_date_by_month] = result.get(checkout_date_by_month, 0) + 1
    logging.debug(f'length of result: {len(result)}')
    if not result:
        logging.error('job did not find anything, empty result')
    return result, group_by_days

def create_chart(result, group_by_days):
    """
        Returns a bar chart with dates and number of bike trips

        Args:
            result (dict): dictionary of dates and counts
    """
    # sort dictionary so plot is in chronological order
    if not group_by_days:
        sorted_keys = sorted(result.keys(), key=lambda x: datetime.strptime(x, '%m/%Y'))
        sorted_values = [result[key] for key in sorted_keys]
    else:
        sorted_keys = sorted(result.keys(), key=lambda x: datetime.strptime(x, '%m/%d/%Y'))
        sorted_values = [result[key] for key in sorted_keys]
    plt.bar(sorted_keys, sorted_values)
    plt.xlabel('Date')
    plt.xticks(rotation=90)
    plt.ylabel('Number of Trips')
    plt.tight_layout()
    plt.savefig('bike_trips_chart.png')


while rd.info()['loading'] == 1: # ensure redis is not loading
    time.sleep(5)

do_work()

