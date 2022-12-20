# Twitter ETL Pipeline

This project main goals was to get 7 days worth of tweets mentioning a text and do some simple transformation over it. All of the data was saved using the Parquet format so that it is ready to be used on a data lake and being a columnar format, other processes can read from it much more effective and cost efficient than other formats. It is also partitioned by day to help on reading only the specified partitions on the transformation. 

It uses Airflow for the pipeline management of tasks and scheduling, using Airflow it is possible to schedule its run automatically using a cron expression and even ad-hoc runs with specified parameters as specified on the DAG (Direct Acyclic Graph) that I am linking below
```python
# mentions: str = "flixbus"
#   string query to use on the Twitter API
#
# extract_date_start: int = now - 7 days
#   timestamp format for the date_start to query data to the twitter API
#
# extract_date_end: int = now
#   timestamp format for the date_end to query data to the twitter API
#
# process_date_start: int = now - 7 days
#   timestamp format to use for the processing on the extracted data
#
# process_date_end: int = now
#   timestamp format to use for the processing on the extracted data
#
```

## Running locally

Before running anything you need to setup an environment file with variables for airflow and the DAG to run correctly, copy the `.env.example` file to a `.env` file using the command
```bash
cp .env.example .env
```
After this you need to access the file and insert your twitter Bearer token on the field `AIRFLOW_VAR_TWITTER_BEARER_TOKEN`

Everything necessary to run it locally is provided on the docker images and it can be easily runned running
```bash
docker-compose up -d
```

After it finishes setting up you can access your `localhost:8080` on your browser and using the default airflow user and password as below
```
user -> airflow
password -> airflow
```