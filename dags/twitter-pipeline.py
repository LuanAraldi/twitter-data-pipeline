import pendulum
import json

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from datetime import datetime, timedelta
import logging

now = pendulum.now("Europe/Berlin")

with DAG(
    dag_id="twitter_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2022, 12, 1, tz="UTC"),
    catchup=False,
    tags=["twitter"],
    default_args={"retries": 5},
    params={
        "date_start": now.subtract(days=7),
        "date_end": now,
        "tweet_query": "flixbus",
    },
) as dag:

    @task(retries=3, retry_delay=timedelta(seconds=20))
    def process_twitter_data(
        date_end: datetime = now, date_start: datetime = now.subtract(days=7)
    ):
        import glob
        import pyarrow as pa
        import pyarrow.parquet as pq
        import pandas as pd

        if date_start > date_end:
            logging.ERROR("End date bigger than start date, not able to process data")

        parquet_partition_file_path = glob.glob("/tmp/data/raw/**/**/*")

        date_to_find = date_start

        partitions_to_read_parquet_files_from = []
        while date_to_find < date_end:
            partition_file_string = f"/tmp/data/raw/year={date_to_find.year}/month={date_to_find.month}/day={date_to_find.day}"
            if partition_file_string in parquet_partition_file_path:
                partitions_to_read_parquet_files_from.append(partition_file_string)
            date_to_find = date_to_find.add(days=1)

        df = pd.concat(
            pd.read_parquet(parquet_file)
            for parquet_file in partitions_to_read_parquet_files_from
        ).drop_duplicates(subset=["text", "author_id", "created_at"])

        def check_if_is_retweet(row):
            if row is None:
                return False
            for referenced_tweet in row:
                if referenced_tweet["type"] == "retweeted":
                    return True
            return False

        df2 = pd.DataFrame().assign(
            text=df["text"],
            user_id=df["author_id"],
            location=df["author.location"],
            number_of_followers=df["author.public_metrics.followers_count"],
            created_at=df["created_at"],
            hashtags=df["entities.hashtags"],
            retweet_count=df["public_metrics.retweet_count"],
            is_retweet=df["referenced_tweets"],
            partition_date=df["created_at"].dt.to_period("D").astype(str),
        )

        df2["is_retweet"] = df2.apply(
            lambda row: check_if_is_retweet(row["is_retweet"]), axis=1
        )

        table = pa.Table.from_pandas(df2)

        logging.info("Writing tweets to parquet file")
        pq.write_to_dataset(
            table, root_path="/tmp/data/processed", partition_cols=["partition_date"]
        )

    @task(retries=3, retry_delay=timedelta(seconds=20))
    def get_twitter_data_by_mention_and_date_range(
        mentions: str = "flixbus",
        date_end: datetime = now,
        date_start: datetime = now.subtract(days=7),
    ):
        from twarc import Twarc2, expansions
        from flatdict import FlatDict
        import pyarrow as pa
        import pyarrow.parquet as pq
        import pandas as pd

        logging.info("Starting to fetch data from Twitter API")
        client = Twarc2(bearer_token=Variable.get("twitter_bearer_token"))
        # End time shenanigans for twitter api without privileged access, end time needs to be 10s before the request time
        end_time = date_end.subtract(seconds=10)
        # Workaroud to get around the non privileged access of getting a 401 after a couple of requests because the start time was bigger than 7 days
        start_time = date_start.add(minutes=5)

        expansion_fields = "referenced_tweets.id,author_id"
        tweet_fields = "created_at,public_metrics,entities"
        user_fields = "location,public_metrics"
        media_fields = "public_metrics"
        query = mentions

        logging.info(
            f"Starting to get tweets with query {query} from {start_time} to {end_time}..."
        )

        tweets_page = client.search_recent(
            query=query,
            start_time=start_time,
            end_time=end_time,
            expansions=expansion_fields,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            media_fields=media_fields,
            max_results=100,
        )

        for page in tweets_page:
            tweets = [
                dict(FlatDict(tweet, delimiter="."))
                for tweet in expansions.flatten(page)
            ]

            for tweet in tweets:
                if tweet.get("referenced_tweets", None):
                    for referenced_tweet in tweet.get("referenced_tweets"):
                        referenced_tweet.pop("author", None)
                        referenced_tweet.pop("referenced_tweets", None)

            df = pd.DataFrame.from_dict(tweets)

            # Partition by year,month,day column insertion
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["year"] = df["created_at"].dt.year
            df["month"] = df["created_at"].dt.month
            df["day"] = df["created_at"].dt.day

            table = pa.Table.from_pandas(df)

            logging.info("Writing tweets to parquet file")
            pq.write_to_dataset(
                table,
                root_path="/tmp/data/raw",
                partition_cols=["year", "month", "day"],
            )

    get_twitter_data_by_mention_and_date_range(
        mentions="{{params.tweet_query}}",
        date_end="{{params.date_end}}",
        date_start="{{params.date_start}}",
    ) >> process_twitter_data(
        date_end="{{params.date_end}}", date_start="{{params.date_start}}"
    )
