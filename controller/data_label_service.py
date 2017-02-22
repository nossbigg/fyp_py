from controller.database_utils import *
from controller.sentiment_utils import *


class DataLabelService:
    config = None
    dbclient = None

    def __init__(self, database_service_class, config_class):
        self.dbclient = database_service_class
        self.config = config_class

    def set_all_sentiments(self):
        db = self.dbclient.get_db()

        # get tweet collection names
        collection_names = get_tweet_collections_only(db.collection_names())

        # iterate through all collections
        for collection_name in collection_names:
            self.set_all_sentiments_collection(collection_name)

    def set_all_sentiments_collection(self, collection_name):
        collection = self.dbclient.get_db()[collection_name]

        cursor = collection.find(
            {},
            {"_id": 1, "text": 1, 'retweeted_status': 1, 'is_quote_status': 1, 'quoted_status_id': 1}
        )

        for tweet in cursor:
            tweet_id = tweet['_id']
            tweet_text = tweet['text']

            tweet_type = get_tweet_type(tweet)
            score_afinn = get_score_afinn(tweet_text)
            score_pos, score_neg, score_obj = get_scores_swn(tweet_text)

            result = collection.update(
                {"_id": tweet_id},
                {'$set': {
                    "tweet_type": tweet_type,
                    "tweet_score_afinn": score_afinn,
                    "tweet_score_swn_pos": score_pos,
                    "tweet_score_swn_neg": score_neg,
                    "tweet_score_swn_obj": score_obj
                }},
                multi=False
            )

            # TODO parallelize afinn labelling process

    def remove_all_sentiments(self):
        db = self.dbclient.get_db()

        # get tweet collection names
        collection_names = db.collection_names()
        collection_names = [name for name in collection_names if not is_links_collection(name)]

        # iterate through all collections
        for collection_name in collection_names:
            self.set_all_sentiments_collection(collection_name)

    def remove_all_sentiments_collection(self, collection_name):
        collection = self.dbclient.get_db()[collection_name]

        result = collection.update(
            {},
            {'$unset': {
                "tweet_type": 1,
                "tweet_score_afinn": 1,
                "tweet_score_swn_pos": 1,
                "tweet_score_swn_neg": 1,
                "tweet_score_swn_obj": 1
            }},
            multi=True
        )
