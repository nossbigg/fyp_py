import pymongo
from controller.database_utils import get_collection_links_name_from_collection_name, get_tweet_collections_only, \
    get_tweet_collections_links_only, gen_unique_tweet_ids_from_links


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

    def get_collection(self, collection_name, db_name=None):
        if db_name is None:
            db_name = self.config.get_db_name()

        return self.dbclient[db_name][collection_name]

    def get_tweet_collections_names_only(self):
        collection_names = self.get_collection_names()
        tweet_collection_names = get_tweet_collections_only(collection_names)

        return tweet_collection_names

    def get_tweet_collections_links_names_only(self):
        collection_names = self.get_collection_names()
        tweet_collection_links_names = get_tweet_collections_links_only(collection_names)

        return tweet_collection_links_names

    def get_unique_tweet_ids_for_collection(self, collection_name, sorted_by_childs_length=False):
        """
        Get unique tweet ids for a given collection
        Allows sorting by tweet's number of child nodes (descending)

        :param collection_name:
        :param sorted_by_childs_length:
        :return:
        """
        collection_links_name = get_collection_links_name_from_collection_name(collection_name)

        query_filter = {"_id": 1, "represented_by_id": 1}
        if sorted_by_childs_length:
            query_filter["childs"] = 1

        cursor = self.get_db()[collection_links_name].find(
            {}, query_filter)
        tweet_links = list(cursor)

        unique_tweet_list = gen_unique_tweet_ids_from_links(tweet_links, sorted_by_childs_length)

        return unique_tweet_list

    def get_unique_tweets_for_collection(self, collection_name, sorted_by_childs_length=False, filter_query=None,
                                         search_query=None):
        """
        Returns unique tweets for a given collection (ie. retrieves single representation per tweet)

        :param collection_name:
        :param sorted_by_childs_length:
        :param filter_query:
        :return:
        """

        unique_tweet_list = self.get_unique_tweet_ids_for_collection(collection_name, sorted_by_childs_length)

        internal_search_query = {"_id": {"$in": unique_tweet_list}}
        if search_query is not None:
            internal_search_query.update(search_query)

        internal_filter_query = {"_id": 1, "text": 1}
        if filter_query is not None:
            internal_filter_query.update(filter_query)

        cursor = self.get_db()[collection_name].find(
            internal_search_query, internal_filter_query)

        return list(cursor)
