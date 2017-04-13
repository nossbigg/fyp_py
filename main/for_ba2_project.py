import csv
import re

import pandas as pd
from controller.config import Config
from controller.data_label_utils import get_all_sentiment_labels
from controller.database_service import DatabaseService
from controller.tweet_csv_label_service import TweetCSVLabelService

config = Config()
dbs = DatabaseService(config)

# combine all known rumor tweets
collection_rumors = ['sickhillary', 'baghdadi_dead', 'death_hoax']
df_rumors = pd.DataFrame()
for collection_name in collection_rumors:
    mongo_search_query = {"tweet_sentiment_label": "s"}
    mongo_filter_query = {"text": 1, "tweet_type": 1, "tweet_sentiment_label": 1}
    mongo_filter_query.update({label: 1 for label in get_all_sentiment_labels()})
    tweets = dbs.get_unique_tweets_for_collection(collection_name, filter_query=mongo_filter_query,
                                                  search_query=mongo_search_query)
    df = pd.DataFrame(tweets)
    df_rumors = df_rumors.append(df)

# combine all known news tweets
collection_news = ['mosul_battle', 'us_economic_policy', 'trump_cabinet']
df_news = pd.DataFrame()
for collection_name in collection_news:
    mongo_search_query = {"tweet_sentiment_label": "s"}
    mongo_filter_query = {"text": 1, "tweet_type": 1, "tweet_sentiment_label": 1}
    mongo_filter_query.update({label: 1 for label in get_all_sentiment_labels()})
    tweets = dbs.get_unique_tweets_for_collection(collection_name, filter_query=mongo_filter_query,
                                                  search_query=mongo_search_query)
    df = pd.DataFrame(tweets)
    df_news = df_news.append(df)
df_news["tweet_sentiment_label"] = ['d' for i in range(0, len(df_news))]

# create news and rumor df
df = pd.DataFrame()
df = df.append(df_rumors)
df = df.append(df_news)

# write to csv
root_csv_dir = config.get_root_dir() + config.get_tweet_csv_label_dir()
csv_label_doc_filepath = \
    TweetCSVLabelService.gen_csv_label_filepath(root_csv_dir, "dataset" + " exported")

CSV_LABEL_FILE_DELIMITER = "|"

tweet_headers = sorted(df.columns.values.tolist())
with open(csv_label_doc_filepath, 'wb') as csv_file:
    writer = csv.writer(csv_file, delimiter=CSV_LABEL_FILE_DELIMITER)
    writer.writerow(tweet_headers)

    for index, tweet in df.iterrows():
        # convert all text fields to utf-8
        for key in tweet_headers:
            value = tweet[key]
            if isinstance(value, basestring):
                tweet[key] = value.encode('utf-8').strip()

        tweet['text'] = re.sub("[\n" + CSV_LABEL_FILE_DELIMITER + "]", "", tweet['text'])

        # to export
        d = []
        for k in tweet_headers:
            if k in tweet:
                d.append(tweet[k])
            else:
                d.append(None)

        writer.writerow(d)
