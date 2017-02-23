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

    def get_unique_tweets_for_collection(self, collection_name, sorted_by_childs_length=False):
        collection_links_name = get_collection_links_name_from_collection_name(collection_name)

        query_filter = {"_id": 1, "represented_by_id": 1}
        if sorted_by_childs_length:
            query_filter["childs"] = 1

        cursor = self.get_db()[collection_links_name].find(
            {}, query_filter)
        tweet_links = list(cursor)

        if sorted_by_childs_length:
            tweet_links.sort(key=lambda tl: len(tl['childs']), reverse=True)

        unique_tweet_list = []
        for doc in tweet_links:
            if doc['represented_by_id'] is None:
                unique_tweet_list.append(doc['_id'])
            else:
                unique_tweet_list.append(doc['represented_by_id'])

        return unique_tweet_list
