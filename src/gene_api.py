from flask import Flask, request, jsonify
import requests
import redis
import json
from jobs import add_job, get_job_by_id, rd, jdb, rdb
import logging
import socket
import os

loglevel = os.environ.get('LOG_LEVEL')
format_str=f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=loglevel, format=format_str)

app = Flask(__name__)

def get_data():
    """
        Load gene dataset
    """
    response = requests.get(url='https://g-a8b222.dd271.03c0.data.globus.org/pub/databases/genenames/hgnc/json/hgnc_complete_set.json')
    return json.loads(response.content)['response']

@app.route('/jobs', methods = ['POST'])
def submit_jobs():
    """
        Route to send a job to redis database

        Methods:
            POST: Send a job to redis database
    """
    data = request.get_json()
    try:
        #logging.debug(f'symbol: {data['symbol']}, gene_group{data['gene_family']}')
        job_dict = add_job(data['gene_group'])
    except KeyError:
        logging.error('invalid parameters, must pass a symbol and a gene_family')
        return jsonify({'message':'invalid parameters, must pass a gene_group'})
    return job_dict

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
        Gets all jobs in the redis database
    """
    #logging.debug(f'Jobs database keys{jdb.keys()}')
    return jsonify(jdb.keys())
@app.route('/jobs/<jobid>', methods=['GET'])
def get_job(jobid):
    """
        Gets a specific job by unique uuid
    """
    try:
        logging.debug(f'job_id: {jobid}')
        return get_job_by_id(jobid)
    except:
        logging.error(f'job_id not found: {jobid}')
        return jsonify({'message': 'job_id not found'})
    
@app.route('/results/<jobid>', methods=['GET'])
def get_result(jobid):
    """
        Return results of a specific job
    """
    try:
        if get_job_by_id(jobid)['status'] != 'complete':
            return jsonify({'message': 'job is not finished yet, try again in a minute'})
        return json.loads(rdb.get(jobid))
    except:
        logging.error(f'job_id not found: {jobid}')
        return jsonify({'message': 'job_id not found'})
    
@app.route('/data', methods=['POST', 'GET', 'DELETE'])
def handle_data():
    """
        Route perfrom POST, GET, DELETE requests on gene dataset

        Methods:
            POST: Load entire dataset into redis database
            GET: Return entire gene dataset from redis database in JSON
            DELETE: Delete everything redis
    """
    if request.method == 'POST':
        try:
            data = get_data()['docs']
            for gene in data:
                rd.set(gene['hgnc_id'], json.dumps(gene))
            logging.debug(f'(POST) Data added successfully')
            return jsonify({'message': 'Data added successfully'})
        except:
            logging.error(f'(POST) Data not found')
            return jsonify({'message': 'Data was NOT added successfully'})
    if request.method == 'GET':
        result = []
        for key in rd.keys():
            result.append(json.loads(rd.get(key)))
        logging.debug(f'(GET) Length of dataset: {len(result)}')
        return jsonify(result)
    if request.method == 'DELETE':
        rd.flushdb()
        return jsonify({'message': 'Data deleted successfully'})

@app.route('/genes', methods=['GET'])
def get_genes():
    """
        Return a list of unique HGNC_IDs
    """
    return jsonify(rd.keys())

@app.route('/genes/<hgnc_id>', methods=['GET'])
def get_specific_gene(hgnc_id):
    """
        Return gene information of a specific HGNC_ID
    """
    if rd.exists(hgnc_id):
        return json.loads(rd.get(hgnc_id))
    logging.error(f'hgnc_id not found: {hgnc_id}')    
    return jsonify({'message': 'hgnc_id not found'})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
