
import pendulum
import json

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from datetime import datetime
import logging

with DAG(
    dag_id="twitter_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2022, 12, 1, tz="UTC"),
    catchup=False,
    tags=["twitter"],
) as dag:

    now = pendulum.now("Europe/Berlin")


    @task()
    def get_twitter_data_by_mention_and_date_range(mentions: str = "flixbus", date_end: datetime = now, date_start: datetime = now.subtract(days=7)):
        
        from twarc import Twarc2, expansions
        from flatdict import FlatDict
        import pandas as pd
        import pyarrow as pa
        import pyarrow.parquet as pq
        

        client = Twarc2(bearer_token=Variable.get('twitter_bearer_token'))
        # End time shenanigans for twitter api without privileged access, end time needs to be 10s before the request time
        end_time = date_end.subtract(seconds=10)
        # Workaroud to get around the non privileged access of getting a 401 after a couple of requests because the start time was bigger than 7 days
        start_time = date_start.add(minutes=5)
        
        expansion_fields = "referenced_tweets.id,author_id"
        tweet_fields = "created_at"
        user_fields = "location"
        media_fields = "public_metrics"
        query = mentions

        logging.info(f"Starting to get tweets with query {query} from {start_time} to {end_time}...")

        tweets_page = client.search_recent(
            query=query, 
            start_time=start_time, 
            end_time=end_time, 
            expansions=expansion_fields,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            media_fields=media_fields,
            max_results=100
        )

        for page in tweets_page:
            tweets = [dict(FlatDict(tweet, delimiter=".")) for tweet in expansions.flatten(page)]

            for tweet in tweets:
                if tweet.get("referenced_tweets", None):
                    for referenced_tweet in tweet.get("referenced_tweets"):
                        referenced_tweet.pop("author", None)
                        referenced_tweet.pop("referenced_tweets", None)

            df = pd.DataFrame.from_dict(tweets)

            #Partition by year,month,day column insertion
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['year'] = df['created_at'].dt.year
            df['month'] = df['created_at'].dt.month
            df['day'] = df['created_at'].dt.day

            table = pa.Table.from_pandas(df)

            logging.info("Writing tweets to parquet file")
            pq.write_to_dataset(
                table,
                root_path='/tmp/data/raw',
                partition_cols=['year', 'month', 'day'],
            )


    

    get_twitter_data_by_mention_and_date_range("flixbus")
