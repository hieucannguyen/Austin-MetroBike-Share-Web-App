import pytest
import requests
import time
import json

def test_handle_data_DELETE():
    response = requests.delete('http://127.0.0.1:5000/data')
    assert response.status_code == 200
    assert response.json()['message'] == 'Data deleted successfully'
    assert isinstance(response.json(), dict) == True
    
def test_handle_data_POST():
    response = requests.post("http://127.0.0.1:5000/data")
    assert response.status_code == 200
    assert response.json()['message'] == 'Data added successfully'
    assert isinstance(response.json(), dict) == True

def test_handle_data_GET():
    response = requests.get("http://127.0.0.1:5000/data?limit=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_submit_jobs():
    data = {"start_date": "05/01/2020","end_date": "06/01/2020"}
    # Convert data to JSON format
    json_data = json.dumps(data)
    response = requests.post("http://127.0.0.1:5000/jobs", 
    data=json_data,
    headers={"Content-Type": "application/json"}
    )
    JOB_ID = response.json()['id']
    assert response.status_code == 200
    assert response.json()['id'] == JOB_ID
    assert isinstance(response.json(), dict) == True

    # jobs GET test
    response = requests.get('http://127.0.0.1:5000/jobs/'+JOB_ID)
    assert response.status_code == 200
    assert response.json()['id'] == JOB_ID
    assert isinstance(response.json(), dict) == True
    
    # jobs result GET test
    time.sleep(600)
    response = requests.get('http://127.0.0.1:5000/download/'+JOB_ID)
    assert response.status_code == 200

def test_get_jobs():
    response = requests.get('http://127.0.0.1:5000/jobs')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_get_trips():
    response = requests.get('http://127.0.0.1:5000/trips')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_get_specific_trip():
    response = requests.get('http://127.0.0.1:5000/trips/19471844')
    assert response.status_code == 200
    assert response.json()['Trip ID'] == '19471844'
    assert isinstance(response.json(), dict) == True

def test_get_bikes():
    response = requests.get('http://127.0.0.1:5000/bikes')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_get_specific_bike():
    response = requests.get('http://127.0.0.1:5000/trips/19471844')
    assert response.status_code == 200
    assert response.json()['hgnc_id'] == 'HGNC:20488'
    assert isinstance(response.json(), dict) == True
