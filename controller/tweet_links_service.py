from controller.database_utils import get_tweet_collections_links_only, get_collection_links_name_from_collection_name, \
    get_tweet_collections_only
from controller.tweet_links_utils import generate_links_dict
from controller.tweet_links_utils import links_dict_to_mongo
from controller.tweet_db_utils import db_tweets_to_tweets_dict


class TweetLinksService:
    config = None
    database_service = None

    def __init__(self, database_service_class, config_class):
        """

        :param config_class: Accepts a ConfigParser object.
        """
        self.database_service = database_service_class
        self.config = config_class

    def gen_all_collection_links(self, overwrite=False):
        collection_names = self.database_service.get_collection_names()
        existing_collections = get_tweet_collections_only(collection_names)

        collection_links_to_create = []

        # if not overwriting, create only dbs without corresponding links dbs
        if overwrite:
            collection_links_to_create = existing_collections
        else:
            existing_links_collections = get_tweet_collections_links_only(collection_names)
            collection_links_to_create = [n for n in existing_collections if
                                          get_collection_links_name_from_collection_name(
                                              n) not in existing_links_collections]

        # generate links dbs
        for collection_name in collection_links_to_create:
            self.gen_collection_link(collection_name, overwrite)

    def gen_collection_link(self, collection_name, overwrite=False):
        db = self.database_service.get_db()
        collection_link_name = get_collection_links_name_from_collection_name(collection_name)

        # if collection link exists and overwrite is true, remove existing collection
        if collection_link_name in self.database_service.get_collection_names():
            if overwrite:
                db[collection_link_name].drop()
            else:
                return

        # get tweets and generate links data
        cursor = db[collection_name].find(
            {},
            {"_id": 1, "id": 1, "tweet_type": 1, "retweeted_status": 1})
        tweets = list(cursor)
        tweets_dict = db_tweets_to_tweets_dict(tweets)
        links_dict = generate_links_dict(tweets_dict)

        # store links
        mongo_items = links_dict_to_mongo(links_dict)
        db[collection_link_name].insert(mongo_items)
