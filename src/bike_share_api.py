from flask import Flask, request, jsonify, send_file
import requests
import redis
import csv
import json
from jobs import add_job, get_job_by_id, rd, jdb, rdb
from datetime import datetime

import logging
import socket
import os

loglevel = os.environ.get('LOG_LEVEL')
format_str=f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=loglevel, format=format_str)

app = Flask(__name__)

def get_data():
    """
        Load bike share dataset. csv -> json
    """
    data = {}
    data['bike_trips'] = []
    with open('Austin_MetroBike_Trips.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data['bike_trips'].append(dict(row))
    return data

@app.route('/help', methods = ['GET'])
def help():
    """
        Route to send information about each endpoint in the API
    """
    return "API Endpoints:\n\n/jobs (POST): Route to send a job to redis database\n/jobs (GET): Gets all jobs in the redis database\n/jobs/<jobid> (GET): Gets the specific job specified by jobid\n/download/<jobid> (GET): Downloads the specific job result specified by jobid\n/data (POST): Put the bike trips dataset into the redis database\n/data (GET): Return all bike trips and their information from the redis database\n/data (DELETE): Delete everything in the redis database\n/trip (GET): Return a list of unique Trip IDs.\n/trip/<trip_id> (GET): Return bike trip information of a specific Trip ID\n/bikes (GET): Return a list of unique Bicycle IDs\n/bikes/<bike_id> (GET) Return trip information of a specific bike_id\n"

@app.route('/jobs', methods = ['POST'])
def submit_jobs():
    """
        Route to send a job to redis database

        Methods:
            POST: Send a job to redis database given a
            json object with a start_date and a end_date parameter
    """
    data = request.get_json()
    try:
        logging.debug(data)
        # ensure correct formatting
        start = datetime.strptime(data['start_date'], '%m/%d/%Y').date()
        end = datetime.strptime(data['end_date'], '%m/%d/%Y').date()
        logging.debug(f'start_date: {start}, end_date: {end}')
        if start >= end: # ensure end date is later than start date
            logging.error('start date cannot be after end date')
            raise Exception()
        job_dict = add_job(data['start_date'], data['end_date'])
        return job_dict
    except:
        logging.error('invalid parameters, must pass a start_date and a end_date')
        return jsonify({'message':'invalid parameters, must pass a start_date and a end_date and start_date must come before end_date'})

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
        Gets all jobs in the redis database
    """
    return jsonify(jdb.keys())
@app.route('/jobs/<jobid>', methods=['GET'])
def get_job(jobid: str):
    """
        Gets a specific job by unique uuid
    """
    try:
        logging.debug(f'job_id: {jobid}')
        return get_job_by_id(jobid)
    except:
        logging.error(f'job_id not found: {jobid}')
        return jsonify({'message': 'job_id not found'})
    
@app.route('/download/<jobid>', methods=['GET'])
def get_chart(jobid: str):
    """
        Downloads results of a specific job
    """
    logging.debug(rdb.keys())
    try:
        if get_job_by_id(jobid)['status'] != 'complete': # ensure job is complete
            return jsonify({'message': 'job is not finished yet, try again in a minute'})
        path = f'{jobid}.png'
        with open(path, 'wb') as f:
            f.write(rdb.hget(jobid, 'image')) # reconstruct data into a png file
        return send_file(path, mimetype='image/png', as_attachment=True) # download file
    except Exception as e:
        logging.error(f'job_id not found: {jobid} ERROR: {e}')
        return jsonify({'message': 'job_id not found'})
    
@app.route('/data', methods=['POST', 'GET', 'DELETE'])
def handle_data():
    """
        Route perfrom POST, GET, DELETE requests on bike trips dataset

        Methods:
            POST: Load entire dataset into redis database
            GET: Return entire bike trip dataset from redis database in JSON
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
        keys = rd.keys()
        try:
            offset = int(request.args.get("offset", 0))
            if offset<0:
                raise ValueError
            limit = int(request.args.get("limit", len(keys)-offset))
            if limit<0:
                raise ValueError
        except ValueError:
            return "Invalid limit or offset parameter; must be a positive integer."
        
        if limit or offset:
            result = []
            for i in range(limit):
                if offset+i>len(keys)-1:
                    return jsonify(result)
                result.append(json.loads(rd.get(keys[offset + i])))
            return jsonify(result)

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
def get_specific_trip(trip_id: str):
    """
        Return trip information of a specific trip_id
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
def get_specific_bike(bike_id: str):
    """
        Return trip information of a specific bike_id
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
