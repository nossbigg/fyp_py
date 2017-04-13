import pandas as pd
from controller.data_label_utils import get_all_sentiment_labels
from pyexcelerate import Workbook
from controller.config import Config
from controller.database_service import DatabaseService

config = Config()
dbs = DatabaseService(config)

excel_save_path = config.get_excel_exports_dir() + "\data.xlsx"
wb = Workbook()

collection_rumors = ['sickhillary', 'baghdadi_dead', 'death_hoax']
collection_news = ['mosul_battle', 'us_economic_policy', 'trump_cabinet']
collection_all = collection_rumors + collection_news

for collection_name in collection_all:
    # get unique tweet list
    unique_tweet_list = dbs.get_unique_tweet_ids_for_collection(collection_name, sorted_by_childs_length=True)

    mongo_search_query = {}
    mongo_filter_query = {"_id": 1, "text": 1, "tweet_type": 1, "tweet_sentiment_label": 1}
    mongo_filter_query.update({label: 1 for label in get_all_sentiment_labels()})

    # save all tweets
    cursor = dbs.get_db()[collection_name].find(mongo_search_query, mongo_filter_query)
    tweets = list(cursor)
    df = pd.DataFrame(tweets)
    data = [df.columns.tolist(), ] + df.values.tolist()
    wb.new_sheet(collection_name, data=data)

    # save unique tweets
    tweets = dbs.get_unique_tweets_for_collection(collection_name, filter_query=mongo_filter_query,sorted_by_childs_length=True)
    df = pd.DataFrame(tweets)
    data = [df.columns.tolist(), ] + df.values.tolist()
    wb.new_sheet(collection_name+" (Unique)", data=data)

wb.save(excel_save_path)
