from flask import Flask, request, jsonify
import requests
import redis
import csv
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
    data = {}
    data['bike_trips'] = []
    with open('..\Austin_MetroBike_Trips.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data['bike_trips'].append(dict(row))
    return data

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
        Route perfrom POST, GET, DELETE requests on bike share dataset

        Methods:
            POST: Load entire dataset into redis database
            GET: Return entire gene dataset from redis database in JSON
            DELETE: Delete everything redis
    """
    if request.method == 'POST':
        try:
            data = get_data()['bike_trips']
            for trip in data:
                rd.set(trip['Trip ID'], json.dumps(trip))
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

@app.route('/trips', methods=['GET'])
def get_trips():
    """
        Return a list of unique TRIP IDs
    """
    return jsonify(rd.keys())

@app.route('/trips/<trip_id>', methods=['GET'])
def get_specific_trip(trip_id):
    """
        Return gene information of a specific trip_id
    """
    if rd.exists(trip_id):
        return json.loads(rd.get(trip_id))
    logging.error(f'trip_id not found: {trip_id}')    
    return jsonify({'message': 'trip_id not found'})

@app.route('/bikes', methods=['GET'])
def get_bikes():
    """
        Return a list of unique Bicycle IDs
    """
    result = set()
    for key in rd.keys():
        result.add(json.loads(rd.get(key))['Bicycle ID'])
    if not result:
        return jsonify({'message': 'Empty Database'})
    result_list = []
    for id in result:
        result_list.append(id)
    return jsonify(result_list)
@app.route('/bikes/<bike_id>', methods=['GET'])
def get_specific_bike(bike_id):
    """
        Return gene information of a specific bike_id
    """
    result = []
    for key in rd.keys():
        trip = json.loads(rd.get(key))
        if trip['Bicycle ID'] == bike_id:
            result.add(trip)
    if not result:
        return jsonify({'message': 'Empty Database'})
    return jsonify(result)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
