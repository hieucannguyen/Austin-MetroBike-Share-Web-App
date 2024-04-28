FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./src/bike_share_api.py ./src/jobs.py ./src/worker.py Austin_MetroBike_Trips.csv ./

CMD ["python3"]
