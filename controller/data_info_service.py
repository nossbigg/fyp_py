import glob
import json
import os

import jsonpickle
from controller.database_utils import get_collection_links_name_from_collection_name
from model.tweet_sentiment_label import TweetSentimentLabel
from model.tweet_type import TweetType


class DataInfoService:
    """
    Generates key statistics about datasets
    """

    config = None
    dbs = None

    def __init__(self, database_service_class, config_class):
        """
        Initialize the Data Info Service.

        :param config_class: Accepts a ConfigParser object.
        """
        self.dbs = database_service_class
        self.config = config_class

    def get_collection_statistic(self, collection_name):
        data = {}

        tweet_collection_links_names = get_collection_links_name_from_collection_name(collection_name)

        collection = self.dbs.get_collection(collection_name)
        collection_links = self.dbs.get_collection(tweet_collection_links_names)

        # number of tweets
        data["tweet_count"] = collection.count({})

        # number of unique tweets
        data["tweet_count_unique"] = collection_links.count({})

        # proportion of tweets by tweet type (eg. tweet, retweet)
        tweet_proportion_type = {}
        for v in [e.value for e in TweetType]:
            tweet_type_count = collection.count({"tweet_type": v})
            if tweet_type_count is not 0:
                tweet_proportion_type[v] = tweet_type_count
        data["tweet_proportion_type"] = tweet_proportion_type

        # proportion of labelled tweets (eg. 30% unlabeled)
        tweet_proportion_labelled = {}
        for v in [e.value for e in TweetSentimentLabel]:
            tweet_labelled_count = collection.count({"tweet_sentiment_label": v})
            if tweet_labelled_count is not 0:
                tweet_proportion_labelled[v] = tweet_labelled_count
        data["tweet_proportion_labelled"] = tweet_proportion_labelled

        # distribution of number of retweets by child
        tweet_distribution_retweet = []
        cursor = collection_links.find({}, {"_id": 1, "childs": 1})
        tweet_links = list(cursor)
        tweet_links.sort(key=lambda tl: len(tl['childs']), reverse=True)
        for tl in tweet_links:
            tl_id = long(tl['_id'])
            count = len(tl['childs'])
            if count <= 10:
                continue
            tweet_distribution_retweet.append([tl_id, count])
        data["tweet_distribution_retweet"] = tweet_distribution_retweet

        # proportion of labelled unique tweets
        unique_tweet_list = self.dbs.get_unique_tweet_ids_for_collection(collection_name)
        tweet_proportion_labelled_unique = {}
        for v in [e.value for e in TweetSentimentLabel]:
            tweet_labelled_count = collection.count({
                "_id": {"$in": unique_tweet_list},
                "tweet_sentiment_label": v})
            if tweet_labelled_count is not 0:
                tweet_proportion_labelled_unique[v] = tweet_labelled_count
        data["tweet_proportion_labelled_unique"] = tweet_proportion_labelled_unique

        return data

    def get_all_statistics(self):
        data = {}

        collection_names = self.dbs.get_tweet_collections_names_only()

        for c in collection_names:
            data[c] = self.get_collection_statistic(c)

        return data

    def get_total_tweet_count(self, collection_name):
        return self.dbs.get_collection(collection_name).count({})

    def get_unique_tweet_count(self, collection_name):
        tweet_collection_links_names = get_collection_links_name_from_collection_name(collection_name)
        return self.dbs.get_collection(tweet_collection_links_names).count({})

    def get_all_ml_results(self):
        data = {}

        ml_test_results_dir = self.config.get_ml_test_results_dir()
        ml_test_results_files = glob.glob(ml_test_results_dir + "/*.json")

        for f in ml_test_results_files:
            head, tail = os.path.split(f)
            filename, ext = tail.split(".")

            with open(f) as data_file:
                json_data = json.load(data_file)

            data[filename] = json_data

        return data
