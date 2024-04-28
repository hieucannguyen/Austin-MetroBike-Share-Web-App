# Gene API Job Requests
This project utilizes the gene symbol reports managed by the HUGO Gene Nomenclature Committee (HGNC) to create API endpoints using flask. The API endpoints serve to perfrom Create, Read, and Delete operations on the HGNC gene dataset to a redis database. The endpoints also support GET routes for users to interact with the gene data from the redis database. Additionally, this project adds a jobs database feature so that user can send in jobs requests and then view results of the job request.

Must have [Docker](https://docs.docker.com/get-docker/) installed on your system.

## ISS Data Overview
The [Human Genome Organization (HUGO) Gene Nomenclature Committee](https://www.genenames.org/download/archive/) provides access to thier gene dataset available in both tab separated and JSON formats. It contains information about approved gene symbols, their associated names, locus groups, locus types, statuses, genomic locations, aliases, previous symbols and names, gene families, and various identifiers such as Entrez Gene ID, Ensembl Gene ID, and UniProt accession numbers, among others.

## File Descriptions
~~~
Homework07/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── README.md
    ├── data
    │   └── .gitcanary
    └── src
      ├── gene_api.py
      ├── jobs.py
      └── worker.py
~~~

- [Dockerfile](Dockerfile) Dockerfile to generate a docker image of our application
- [docker-compose.yml](docker-compose.yml) docker-compose file to run the containerized Flask application
- [requirements.txt](requirements.txt) Required dependencies for the project
- [gene_api.py](gene_api.py) API endpoints for communicaton to redis and get requests
- [jobs.py](jobs.py) Module to handle jobs requests 
- [worker.py](worker.py) worker to handle jobs in the redis database (queue) as they come in and then post results in the results database

## Running the application using Docker
### Build the image
Navigate into the directory where our app, Dockerfile, and [docker-compose.yml](docker-compose.yml) are located.

Run 
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

## API Endpoints

### `/jobs`
- METHOD: POST
- Put the job request into the redis database.

Example output using `$ curl localhost:5000/jobs -X POST -d '{"symbol": "AA","gene_family":123}' -H "Content-Type: application/json"`:
~~~
{
  "gene_group": "Antisense RNAs",
  "id": "a9935554-878e-437b-a3fe-25f15c0b1788",
  "status": "submitted",
}
~~~
Means the job has been added to the redis database successfully.
### `/jobs`
- METHOD: GET
- Gets all the current/past jobs in the redis database

Example output using `$ curl localhost:5000/jobs`:
~~~
[
  "b6520382-e89b-4ad6-9340-143d61a6268f",
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
  "gene_group": "Antisense RNAs",
  "id": "a9935554-878e-437b-a3fe-25f15c0b1788",
  "status": "complete"
}
~~~
*Status could also report in progess meaning the job hasn't finished yet.*
### `/results/<jobid>`
- METHOD: GET
- Gets the specific job result specified by jobid

Example output using `$ curl localhost:5000/results/a9935554-878e-437b-a3fe-25f15c0b1788`:
~~~
{
  "1998": 2,
  "2000": 6,
  "2001": 12,
  "2002": 3,
  "2003": 13,
  "2004": 26,
  "2005": 30,
  "2006": 14,
  "2007": 12,
  "2008": 11,
  "2009": 14,
  "2010": 10,
  "2011": 364,
  "2012": 206,
  "2013": 147,
  "2014": 197,
  "2015": 33,
  "2016": 32,
  "2017": 87,
  "2018": 56,
  "2019": 148,
  "2020": 152,
  "2021": 220,
  "2022": 98,
  "2023": 46
}
~~~
This result is when a gene of a specified group was first approved and ordered by date.
### `/data`
- METHOD: POST
- Put the gene dataset into the redis database.

Example output using `$ curl localhost:5000/data -X POST`:
~~~
{
  "message": "Data added successfully"
}
~~~
Means the data has been added to the redis database successfully.
### `/data`
- METHOD: GET
- Return all genes and their information from the redis database.

Example output using `$ curl localhost:5000/data`:
~~~
[
  {
    "hgnc_id": "HGNC:23495",
    ...
  },
  {
    "hgnc_id": "HGNC:46894",
    ...
  },
  ...
]
~~~
Where each dictionary (looks like [/genes/<hgnc_id> GET route](#/genes/<hgnc_id>)) in the list is a gene with its associated data.
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
### `/genes`
- METHOD: GET
- Return a list of unique HGNC_IDs.

Example output using `$ curl localhost:5000/genes`:
~~~
[
  "HGNC:14452",
  "HGNC:18414",
  "HGNC:30781",
  "HGNC:22125",
  "HGNC:19385",
  "HGNC:18370",
  "HGNC:14299",
  "HGNC:23495",
  ...
]
~~~
### `/genes/<hgnc_id>`
- METHOD: GET
- Return gene information of a specific HGNC_ID.

Example output using `$ curl localhost:5000/genes/HGNC:20488`:
~~~
{
  "_version_": 1793942604439617536,
  "agr": "HGNC:20488",
  "alias_symbol": [
    "FLJ25436"
  ],
  "ccds_id": [
    "CCDS9739"
  ],
  "date_approved_reserved": "2004-06-11",
  "date_modified": "2023-01-20",
  "date_name_changed": "2016-03-24",
  "date_symbol_changed": "2012-08-15",
  "ena": [
    "AI762327"
  ],
  "ensembl_gene_id": "ENSG00000126790",
  "entrez_id": "112849",
  "enzyme_id": [
    "4.2.1.77"
  ],
  "hgnc_id": "HGNC:20488",
  "location": "14q23.1",
  "location_sortable": "14q23.1",
  "locus_group": "protein-coding gene",
  "locus_type": "gene with protein product",
  "mane_select": [
    "ENST00000247194.9",
    "NM_144581.2"
  ],
  "mgd_id": [
    "MGI:1914467"
  ],
  "name": "trans-L-3-hydroxyproline dehydratase",
  "omim_id": [
    "614811"
  ],
  "prev_name": [
    "chromosome 14 open reading frame 149",
    "L-3-hydroxyproline dehydratase (trans-)"
  ],
  "prev_symbol": [
    "C14orf149"
  ],
  "pubmed_id": [
    22528483
  ],
  "refseq_accession": [
    "NM_144581"
  ],
  "rgd_id": [
    "RGD:1305721"
  ],
  "status": "Approved",
  "symbol": "L3HYPDH",
  "ucsc_id": "uc001xee.2",
  "uniprot_ids": [
    "Q96EM0"
  ],
  "uuid": "1b4830b4-1875-4072-9793-114d6996f428",
  "vega_id": "OTTHUMG00000028941"
}
~~~
