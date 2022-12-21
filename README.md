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

## Sample Data collected
### Raw data
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>author_id</th>
      <th>referenced_tweets</th>
      <th>entities.hashtags</th>
      <th>entities.annotations</th>
      <th>entities.urls</th>
      <th>entities.mentions</th>
      <th>created_at</th>
      <th>edit_history_tweet_ids</th>
      <th>text</th>
      <th>id</th>
      <th>...</th>
      <th>author.name</th>
      <th>author.public_metrics.followers_count</th>
      <th>author.public_metrics.following_count</th>
      <th>author.public_metrics.tweet_count</th>
      <th>author.public_metrics.listed_count</th>
      <th>author.username</th>
      <th>__twarc.url</th>
      <th>__twarc.version</th>
      <th>__twarc.retrieved_at</th>
      <th>author.location</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>991241390335049728</td>
      <td>[{'author_id': '104524555', 'created_at': '202...</td>
      <td>[{'end': 132, 'start': 127, 'tag': 'フランス'}, {'...</td>
      <td>[{'end': 23, 'normalized_text': 'YouTube', 'pr...</td>
      <td>[{'description': '2022年9～10月のフランス旅の8回目（最終回）です。...</td>
      <td>[{'end': 15, 'id': '104524555', 'location': '日...</td>
      <td>2022-12-14 11:12:11+00:00</td>
      <td>[1602984792894500865]</td>
      <td>RT @musyokutabi: YouTubeに動画をアップロードしました\n⇒【フランス...</td>
      <td>1602984792894500865</td>
      <td>...</td>
      <td>🍁もみじ🍁</td>
      <td>27</td>
      <td>94</td>
      <td>6678</td>
      <td>0</td>
      <td>TrsRxPQjc8p6Q62</td>
      <td>https://api.twitter.com/2/tweets/search/recent...</td>
      <td>2.12.0</td>
      <td>2022-12-20T21:16:02+00:00</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>104524555</td>
      <td>None</td>
      <td>[{'end': 115, 'start': 110, 'tag': 'フランス'}, {'...</td>
      <td>[{'end': 6, 'normalized_text': 'YouTube', 'pro...</td>
      <td>[{'description': '2022年9～10月のフランス旅の8回目（最終回）です。...</td>
      <td>[{'end': 106, 'id': '10228272', 'location': No...</td>
      <td>2022-12-14 11:07:29+00:00</td>
      <td>[1602983611678195715]</td>
      <td>YouTubeに動画をアップロードしました\n⇒【フランス旅2022】夜のパリ北駅はやっぱり...</td>
      <td>1602983611678195715</td>
      <td>...</td>
      <td>無職旅</td>
      <td>10895</td>
      <td>143</td>
      <td>21925</td>
      <td>64</td>
      <td>musyokutabi</td>
      <td>https://api.twitter.com/2/tweets/search/recent...</td>
      <td>2.12.0</td>
      <td>2022-12-20T21:16:02+00:00</td>
      <td>日本</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1633016234</td>
      <td>[{'author_id': '294521181', 'created_at': '202...</td>
      <td>[{'end': 40, 'start': 25, 'tag': 'Weihnachtsze...</td>
      <td>None</td>
      <td>None</td>
      <td>[{'end': 14, 'id': '294521181', 'location': 'M...</td>
      <td>2022-12-14 11:05:54+00:00</td>
      <td>[1602983210832601090]</td>
      <td>RT @FlixBus_DE: Über die #Weihnachtszeit sind ...</td>
      <td>1602983210832601090</td>
      <td>...</td>
      <td>Bus Blickpunkt</td>
      <td>405</td>
      <td>274</td>
      <td>3377</td>
      <td>15</td>
      <td>bus_blickpunkt</td>
      <td>https://api.twitter.com/2/tweets/search/recent...</td>
      <td>2.12.0</td>
      <td>2022-12-20T21:16:02+00:00</td>
      <td>64625 Bensheim</td>
    </tr>
    <tr>
      <th>3</th>
      <td>294521181</td>
      <td>None</td>
      <td>[{'end': 24, 'start': 9, 'tag': 'Weihnachtszei...</td>
      <td>None</td>
      <td>[{'description': None, 'display_url': 'pic.twi...</td>
      <td>None</td>
      <td>2022-12-14 11:01:54+00:00</td>
      <td>[1602982206598795264]</td>
      <td>Über die #Weihnachtszeit sind mehr grüne Busse...</td>
      <td>1602982206598795264</td>
      <td>...</td>
      <td>Flix News</td>
      <td>8594</td>
      <td>577</td>
      <td>17331</td>
      <td>89</td>
      <td>FlixBus_DE</td>
      <td>https://api.twitter.com/2/tweets/search/recent...</td>
      <td>2.12.0</td>
      <td>2022-12-20T21:16:02+00:00</td>
      <td>Munich, Germany</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1432423963</td>
      <td>[{'author_id': '702553804265398273', 'created_...</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>[{'end': 15, 'id': '702553804265398273', 'loca...</td>
      <td>2022-12-14 11:00:22+00:00</td>
      <td>[1602981818621644800]</td>
      <td>@_brix_designer @FlixBus_DE Machst du ne arben...</td>
      <td>1602981818621644800</td>
      <td>...</td>
      <td>Tempi93</td>
      <td>118</td>
      <td>206</td>
      <td>12034</td>
      <td>4</td>
      <td>Tempi93</td>
      <td>https://api.twitter.com/2/tweets/search/recent...</td>
      <td>2.12.0</td>
      <td>2022-12-20T21:16:02+00:00</td>
      <td>Region Hannover</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 25 columns</p>
</div>

### Processed data

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>text</th>
      <th>user_id</th>
      <th>location</th>
      <th>number_of_followers</th>
      <th>created_at</th>
      <th>hashtags</th>
      <th>retweet_count</th>
      <th>is_retweet</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>@AmreiBahr @DB_Bahn 9) Fahrt besser mit dem Fl...</td>
      <td>1144614159461601283</td>
      <td>NRW</td>
      <td>146</td>
      <td>2022-12-13 23:29:59+00:00</td>
      <td>None</td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>FlixBus lança viagens entre Minas e São Paulo ...</td>
      <td>1519315928080695297</td>
      <td>None</td>
      <td>0</td>
      <td>2022-12-13 23:29:29+00:00</td>
      <td>None</td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>@itsmightymikeee @MinIenW Dan is dat theoriebo...</td>
      <td>247862097</td>
      <td>Groningen, Nederland</td>
      <td>1377</td>
      <td>2022-12-13 23:18:48+00:00</td>
      <td>None</td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>3</th>
      <td>@jooohnas @arcaico17 Olha\nTem história de oni...</td>
      <td>3566900902</td>
      <td>Rio de Janeiro, Brasil</td>
      <td>42</td>
      <td>2022-12-13 23:06:45+00:00</td>
      <td>None</td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>4</th>
      <td>@flixbus_uk @CPT_UK @TfL Your company is shit ...</td>
      <td>1535172714373193728</td>
      <td>None</td>
      <td>0</td>
      <td>2022-12-13 22:59:59+00:00</td>
      <td>None</td>
      <td>0</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>
