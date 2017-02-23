import pymongo
from controller.database_utils import get_collection_links_name_from_collection_name


class DatabaseService:
    dbclient = None
    config = None

    def __init__(self, config_class):
        self.config = config_class
        self.dbclient = pymongo.MongoClient()

    def get_db(self, db_name=None):
        if db_name is None:
            db_name = self.config.get_db_name()

        return self.dbclient[db_name]

    def get_collection_names(self, db_name=None):
        if db_name is None:
            db_name = self.config.get_db_name()

        return self.dbclient[db_name].collection_names()

    def get_unique_tweets_for_collection(self, collection_name):
        collection_links_name = get_collection_links_name_from_collection_name(collection_name)

        cursor = self.get_db()[collection_links_name].find(
            {},
            {"_id": 1, "represented_by_id": 1})
        tweet_links = list(cursor)

        unique_tweet_list = []
        for doc in tweet_links:
            if doc['represented_by_id'] is not None:
                unique_tweet_list.append(doc['represented_by_id'])
            else:
                unique_tweet_list.append(doc['_id'])

        return unique_tweet_list
