import csv
import glob
import os

import re

from controller.database_utils import get_collection_links_name_from_collection_name
from controller.tweet_links_utils import gen_represented_by_reverse_lookup_dict, gen_peer_tweet_ids
from controller.tweet_links_utils import gen_tweet_links_dict
from model.tweet_sentiment_label import TweetSentimentLabel
from controller.tweet_db_utils import db_tweets_to_tweets_dict

CSV_LABEL_FILE_DELIMITER = '|'


class TweetCSVLabelService:
    config = None
    database_service = None

    def __init__(self, database_service_class, config_class):
        """

        :param config_class: Accepts a ConfigParser object.
        """
        self.database_service = database_service_class
        self.config = config_class

    def gen_csv_label_docs(self, overwrite=False, exclude_labelled=True):
        collection_names = self.database_service.get_tweet_collections_names_only()
        collections_to_process = collection_names

        if not overwrite:
            root_csv_dir = self.config.get_root_dir() + self.config.get_tweet_csv_label_dir()
            collections_to_process = [n for n in collection_names if not os.path.exists(
                self.gen_csv_label_filepath(root_csv_dir, n))]

        for collection_name in collections_to_process:
            self.gen_csv_label_doc(collection_name, overwrite, exclude_labelled)

    def gen_csv_label_doc(self, collection_name, overwrite=False, exclude_labelled=True):
        root_csv_dir = self.config.get_root_dir() + self.config.get_tweet_csv_label_dir()
        csv_label_doc_filepath = \
            self.gen_csv_label_filepath(root_csv_dir, collection_name)

        # get unique tweets by largest number of childs
        unique_tweet_ids = self.database_service.get_unique_tweet_ids_for_collection(collection_name, True)

        # if exclude labelled, exclude tweets that are already labelled
        find_criteria = {"_id": {"$in": unique_tweet_ids}}
        if exclude_labelled:
            find_criteria["tweet_sentiment_label"] = {"$eq": None}

        cursor = self.database_service.get_collection(collection_name).find(
            find_criteria,
            {"text": 1, "_id": 1, "tweet_type": 1}
        )
        tweets = list(cursor)
        tweets_dict = db_tweets_to_tweets_dict(tweets)

        # if filex exists and overwrite is false, stop
        if not overwrite and os.path.exists(csv_label_doc_filepath):
            return

        # write csv
        with open(csv_label_doc_filepath, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=CSV_LABEL_FILE_DELIMITER)
            writer.writerow(self.get_tweet_csv_label_format())
            count = 1
            for tweet_id in unique_tweet_ids:
                # skip if tweet not found
                if tweet_id not in tweets_dict:
                    continue

                tweet = tweets_dict[tweet_id]

                tweet['text'] = tweet['text'].encode('utf-8').strip()
                tweet['text'] = re.sub("[\n" + CSV_LABEL_FILE_DELIMITER + "]", "", tweet['text'])

                tweet_data_to_export = [tweet[field] for field in self.get_tweet_csv_label_format()[2:]]
                writer.writerow([count, ''] + tweet_data_to_export)
                count += 1

    def import_csv_label_docs(self, overwrite=False):
        root_csv_dir = self.config.get_root_dir() + self.config.get_tweet_csv_label_dir()
        csv_paths = glob.glob(root_csv_dir + "/*.csv")

        for path in csv_paths:
            self.import_csv_label_doc(path, overwrite)

    def import_csv_label_doc(self, csv_filepath, overwrite=False):
        collection_name = self.get_collection_name_from_csv_filepath(csv_filepath)

        # stop if collection does not exist
        if collection_name not in self.database_service.get_collection_names():
            return

        collection = self.database_service.get_collection(collection_name)

        # get links information
        collection_link_name = get_collection_links_name_from_collection_name(collection_name)
        cursor = self.database_service.get_collection(collection_link_name).find({})
        tweet_links_dict = gen_tweet_links_dict(list(cursor))
        retweet_reverse_lookup_list = gen_represented_by_reverse_lookup_dict(tweet_links_dict.values())

        with open(csv_filepath, 'rb') as csv_file:
            is_first_row = True
            for line in csv_file:
                line = line.strip()

                # skip header row, skip empty lines
                if is_first_row or len(line) == 0:
                    is_first_row = False
                    continue

                self.__import_csv_label_entry(line, collection, tweet_links_dict, retweet_reverse_lookup_list,
                                              overwrite)

    def __import_csv_label_entry(self, csv_line, collection, tweet_links_dict, retweet_reverse_lookup_list,
                                 overwrite=False):
        # form csv label entry data structure
        entry = {}
        row_data = csv_line.split(CSV_LABEL_FILE_DELIMITER)

        # skip if improper format
        try:
            for count, field in enumerate(self.get_tweet_csv_label_format()):
                entry[field] = row_data[count]
            entry['_id'] = long(entry['_id'])
        except ValueError or IndexError:
            return

        # skip if invalid sentiment
        try:
            TweetSentimentLabel(entry['tweet_sentiment_label'])
        except ValueError:
            return

        # skip if has existing labelled tweet
        tweet_id = entry['_id']
        if not overwrite:
            matching_records_num = collection.count(
                {"_id": tweet_id,
                 "tweet_sentiment_label": {"$exists": True}})
            if matching_records_num > 0:
                return

        # update peers/childs also
        ids_to_update = [tweet_id] + gen_peer_tweet_ids(tweet_id, tweet_links_dict, retweet_reverse_lookup_list)

        # label tweet
        collection.update(
            {"_id": {"$in": ids_to_update}},
            {'$set': {"tweet_sentiment_label": entry['tweet_sentiment_label']}},
            multi=True)

    def export_csv_label_doc(self, collection_name):
        root_csv_dir = self.config.get_root_dir() + self.config.get_tweet_csv_label_dir()
        csv_label_doc_filepath = \
            self.gen_csv_label_filepath(root_csv_dir, collection_name + " exported")

        # get unique tweets by largest number of childs
        unique_tweet_ids = self.database_service.get_unique_tweet_ids_for_collection(collection_name, True)

        # export labelled tweets only
        find_criteria = {"_id": {"$in": unique_tweet_ids},
                         "tweet_sentiment_label": {"$exists": True}}

        cursor = self.database_service.get_collection(collection_name).find(
            find_criteria
                      )
        tweets = list(cursor)

        # generate headers
        tweet_headers = sorted(tweets[0].keys())
        tweet_headers = [k.encode('utf-8') for k in tweet_headers]

        # write csv
        with open(csv_label_doc_filepath, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=CSV_LABEL_FILE_DELIMITER)
            writer.writerow(tweet_headers)

            for tweet in tweets:
                # convert all text fields to utf-8
                for key, value in tweet.iteritems():
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

    @staticmethod
    def gen_csv_label_filepath(root_dir, collection_name):
        return root_dir + "\\" + collection_name + ".csv"

    @staticmethod
    def get_collection_name_from_csv_filepath(csv_filepath):
        filename_w_extension = os.path.basename(csv_filepath)
        collection_name = os.path.splitext(filename_w_extension)[0]

        collection_name = re.sub("\([a-zA-Z0-9]*?\)$", "", collection_name)

        return collection_name

    @staticmethod
    def get_tweet_csv_label_format():
        return ['count', 'tweet_sentiment_label', 'text', '_id', 'tweet_type']
