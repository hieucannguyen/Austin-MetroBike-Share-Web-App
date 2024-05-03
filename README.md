# Austin MetroBikeShare Web App
This project utilizes the Austin MetroBike Trips dataset managed by the City of Austin open data portal to create API endpoints using flask. The API endpoints serve to perfrom Create, Read, and Delete operations on the MetroBike Trips dataset to a redis database. The endpoints also support GET routes for users to interact with the MetroBike data from the redis database. Additionally, this project adds a jobs database feature so that user can send in jobs requests and then view results of the job request.

This project also uses Docker and kubernetes to deploy the Web App making it portable and available for anyone to use.

Must have [Docker](https://docs.docker.com/get-docker/) and [kubernetes](https://kubernetes.io/releases/download/) installed on your system.

## Austin MetroBike Trips Data Overview
The [City of Austin open data portal](https://data.austintexas.gov/Transportation-and-Mobility/Austin-MetroBike-Trips/tyfh-5r8s/about_data) provides access to the Austin MetroBike Trips dataset available in both CSV and JSON formats, but is limited to 1000 rows of data through their endpoint. Instead we will download the data as a whole using their download feature. Overall, the dataset contains information about bike trips, their associated trip IDs, membership type, bicycle IDs, bicycle types, checkout times, trip duration, and kiosk location, among others.

## File Descriptions
~~~
Austin-MetroBike-Share-Web-App/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── software_diagram.svg
    ├── README.md
    ├── kubernetes
    ├── prod
    │   ├── app-prod-deployment-flask.yml
    │   ├── app-prod-deployment-redis.yml
    │   ├── app-prod-deployment-worker.yml
    │   ├── app-prod-ingress-flask.yml
    │   ├── app-prod-pvc-redis.yml
    │   ├── app-prod-service-flask.yml
    │   ├── app-prod-service-nodeport-flask.yml
    │   └── app-prod-service-redis.yml
    └── test
    │   ├── app-test-deployment-flask.yml
    │   ├── app-test-deployment-redis.yml
    │   ├── app-test-deployment-worker.yml
    │   ├── app-test-ingress-flask.yml
    │   ├── app-test-pvc-redis.yml
    │   ├── app-test-service-flask.yml
    │   ├── app-test-service-nodeport-flask.yml
    │   └── app-test-service-redis.yml
    ├── data
    │   └── .gitcanary
    ├── test
    │   └── bike_share_api.py
    └── src
      ├── bike_share_api.py
      ├── jobs.py
      └── worker.py
~~~

- [Dockerfile](Dockerfile) Dockerfile to generate a docker image of our application
- [docker-compose.yml](docker-compose.yml) docker-compose file to run the containerized Flask application
- [requirements.txt](requirements.txt) Required dependencies for the project
- [bike_share_api.py](./src/bike_share_api.py) API endpoints for communicaton to redis, jobs, and GET requests
- [jobs.py](./src/jobs.py) Module to handle jobs requests 
- [worker.py](./src/worker.py) worker to handle jobs in the redis database (queue) as they come in and then post results (plots) in the results database
- [test_gene_api.py](./test/test_gene_api.py) Integration tests for flask app

## Software Diagram
![image](diagram.svg)

*Software diagram of the Flask Application. Visualization of the containerized application using Docker and how the Flask app interacts with worker and Redis container.*

## Running the application using Docker
### Build the image

**IMPORTANT**

Before we run the application we must import the dataset. Navigate into the directory where our Dockerfile, and [docker-compose.yml](docker-compose.yml) are located and run this command to download the dataset.
~~~
$ wget https://data.austintexas.gov/api/views/tyfh-5r8s/rows.csv?accessType=DOWNLOAD -O Austin_MetroBike_Trips.csv
~~~

Now run 
~~~
$ docker-compose build
~~~

### Run Flask Application Container
Using the [docker-compose.yml](docker-compose.yml) file we can use it to start the Flask application container
~~~
$ docker-compose up -d
~~~
**Note:** -d starts the application in the background

Since we mapped to port 5000 in the [docker-compose.yml](docker-compose.yml) to interact with the Flask endpoints we can use `curl localhost:5000/...`

To stop the container use
~~~
$ docker-compose down
~~~
## Kubernetes Deployment
### Deploy
~~~
$ kubectl apply -f kubernetes/prod/
~~~
### Using Web App
Using the ingress
~~~
$ curl http://hieucannguyen.coe332.tacc.cloud/<route>
~~~
See [API Endpoints](#api-endpoints) for different routes.
## API Endpoints

### `/jobs`
- METHOD: POST
- Put the job request into the redis database.

Example output using `$ curl localhost:5000/jobs -X POST -d '{"start_date": "05/01/2022","end_date": "05/01/2023"}' -H "Content-Type: application/json"`:
~~~
{
  "end_date": "05/01/2023",
  "id": "a69f7bc1-f0eb-456d-94d8-a78bf17862c0",
  "start_date": "05/01/2022",
  "status": "submitted"
}
~~~
This means the job has been added to the redis database successfully. Also given start and end date parameters this job will output a bar chart allowing users to visualize the number of bike trips over a period of time
### `/jobs`
- METHOD: GET
- Gets all the current/past jobs in the redis database

Example output using `$ curl localhost:5000/jobs`:
~~~
[
  "a69f7bc1-f0eb-456d-94d8-a78bf17862c0",
  "523451d4-b46a-44d9-ad24-27900a3e0412",
  "d5ae5cc8-67e1-41e6-abfc-a19cc2d1bf4d",
  "48b10aa6-0133-47e3-b650-4f9fe1191931",
  "15fa79db-a093-4ba4-8ace-d7968f77d9ea",
  "c62cd254-c67d-467f-b317-357477611dc0",
  "eaaba65c-56b5-40c6-81d0-5ed6197e21ec"
]
~~~
Means the data has been added to the redis database successfully.
### `/jobs/<jobid>`
- METHOD: GET
- Gets the specific job specified by jobid

Example output using `$ curl localhost:5000/jobs/a9935554-878e-437b-a3fe-25f15c0b1788`:
~~~
{
  "end_date": "05/01/2023",
  "id": "a69f7bc1-f0eb-456d-94d8-a78bf17862c0",
  "start_date": "05/01/2022",
  "status": "complete"
}
~~~
*Status could also report in progess meaning the job hasn't finished yet.*
### `/download/<jobid>`
- METHOD: GET
- Downloads the specific job result specified by jobid

Example output using `$ curl localhost:5000/download/a69f7bc1-f0eb-456d-94d8-a78bf17862c0 --output output.png`:
*The --output output.png downloads the plot as output.png*
~~~
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 14245  100 14245    0     0  3024k      0 --:--:-- --:--:-- --:--:-- 3477k
~~~
Plot has downloaded.
### `/data`
- METHOD: POST
- Put the bike trip dataset into the redis database.

Example output using `$ curl localhost:5000/data -X POST`:
~~~
{
  "message": "Data added successfully"
}
~~~
Means the data has been added to the redis database successfully.
### `/data`
- METHOD: GET
- Return all bike trips and their information from the redis database.

Example output using `$ curl localhost:5000/data`:
~~~
[
  {
    "trip_id": "29745510",
    ...
  },
  {
    "trip_id": "29550686",
    ...
  },
  ...
]
~~~
Where each dictionary (looks like [/trip/<trip_id> GET route](#triptrip_id)) in the list is a bikr trip with its associated data.
### `/data`
- METHOD: DELETE
- Delete everything in the redis database

Example output using `$ curl localhost:5000/data -X DELETE`:
~~~
{
  "message": "Data deleted successfully"
}
~~~
Where data was deleted successfully
### `/trip`
- METHOD: GET
- Return a list of unique Trip IDs.

Example output using `$ curl localhost:5000/trip`:
~~~
[
  "29550686",
  "29667683",
  "29632824",
  "29504815",
  "29678294",
  ...
]
~~~
### `/trip/<trip_id>`
- METHOD: GET
- Return bike trip information of a specific Trip ID.

Example output using `$ curl localhost:5000/trip/HGNC:20488`:
~~~
  {
    "Trip ID": "29632824",
    "Membership or Pass Type": "Local365",
    "Bicycle ID": "21455",
    "Bike Type": "electric",
    "Checkout Datetime": "2023-05-15T17:12:36.000",
    "Checkout Date": "2023-05-15T00:00:00.000",
    "Checkout Time": "17:12:36",
    "Checkout Kiosk Id": "2499",
    "Checkout Kiosk": "2nd/Lavaca @ City Hall",
    "Return Kiosk Id": "2499",
    "Return Kiosk": "South Congress/Elizabeth",
    "Trip Duration Minutes": "8",
    "Month": "5",
    "Year": "2023"
  }
~~~
