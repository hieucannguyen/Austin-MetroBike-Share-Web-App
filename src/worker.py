from jobs import get_job_by_id, update_job_status, q, rd, rdb
import json
import logging
from datetime import datetime

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
    # get genes specified by group
    genes = get_genes_by_groups(job['gene_group'])
    date_freq = {}
    for gene in genes:
        if gene.get('date_approved_reserved'): # none value handling
            date_object = datetime.strptime(gene['date_approved_reserved'], '%Y-%m-%d').date() # extract time
            year = date_object.strftime('%Y') # extract year
            date_freq[year] = date_freq.get(year, 0) + 1
    logging.debug(f'length of result: {len(date_freq)}')
    if not date_freq:
        logging.error('job did not find anything, empty result')
    rdb.set(jobid, json.dumps(date_freq)) # input to results database
    update_job_status(jobid, 'complete') # update job database

def get_genes_by_groups(group):
    """
        Returns a list of genes specified by a gene group

        Args:
            group (string): specific gene group
    """
    result = []
    for key in rd.keys():
        gene = json.loads(rd.get(key))
        if gene.get('gene_group'): # none value handling
            for g in gene.get('gene_group'):
                if g == group:
                    result.append(gene)
    logging.debug(f'length of result: {len(result)}')
    if not result:
        logging.error('job did not find anything, empty result')
    return result

do_work()

