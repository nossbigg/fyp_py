import nltk
from afinn import Afinn
from controller.database_utils import *
from controller.sentiment_utils import *
from controller.tweet_llinks_utils import gen_represented_by_reverse_lookup_dict, gen_peer_tweet_ids, \
    gen_tweet_links_dict


class DataLabelService:
    config = None
    dbclient = None

    __nps_corpus_retrieved = None
    __pos_tagger_nps = None
    __afinn_default = None
    __tokenizer_default = None
    __nps_tag_convert_dict = None

    def __init__(self, database_service_class, config_class):
        self.dbclient = database_service_class
        self.config = config_class

        # Initialize nps tagger
        self.__nps_corpus_retrieved = get_nltk_nps_corpus()
        self.__pos_tagger_nps = nltk.UnigramTagger(self.__nps_corpus_retrieved)
        self.__nps_tag_convert_dict = get_nps_tag_convert_dict(
            self.config.get_root_dir() + self.config.get_nps_tag_convert_filepath())

        # Initialize afinn
        self.__afinn_default = Afinn()

        # Initialize tokenizer
        self.__tokenizer_default = nltk.TweetTokenizer(preserve_case=False,
                                                       reduce_len=False, strip_handles=False)

    def set_all_sentiments(self):
        db = self.dbclient.get_db()

        # get tweet collection names
        collection_names = get_tweet_collections_only(db.collection_names())

        # iterate through all collections
        for collection_name in collection_names:
            self.set_all_sentiments_collection(collection_name)

    def set_all_sentiments_collection(self, collection_name):
        """
        Set text sentiment scores
        Utilizes tweet links db to speed up process

        :param collection_name:
        :return:
        """
        # get links information
        collection_link_name = get_collection_links_name_from_collection_name(collection_name)
        cursor = self.dbclient.get_collection(collection_link_name).find({})
        tweet_links_dict = gen_tweet_links_dict(list(cursor))
        retweet_reverse_lookup_list = gen_represented_by_reverse_lookup_dict(tweet_links_dict.values())

        # get cursor to label tweets
        unique_tweet_list = gen_unique_tweet_ids_from_links(tweet_links_dict.values())
        collection = self.dbclient.get_collection(collection_name)
        cursor = collection.find(
            {"_id": {"$in": unique_tweet_list}},
            {"_id": 1, "text": 1, 'tweet_type': 1})

        # set normalize variable
        normalize_features = False

        for tweet in cursor:
            tweet_id = tweet['_id']
            tweet_text = tweet['text']

            # TODO might consider preprocessing text before scoring text
            text_tokens = self.__tokenizer_default.tokenize(tweet_text)

            # afinn
            score_afinn = get_score_afinn(tweet_text, self.__afinn_default)
            # swn
            score_pos, score_neg, score_obj = get_scores_swn(text_tokens, normalize=normalize_features)
            # nltk pos
            pos_dict = get_pos_tags(text_tokens, self.__pos_tagger_nps, self.__nps_tag_convert_dict,
                                    normalize=normalize_features)
            pos_dict_mongo = pos_tags_universal_to_mongo_dict(pos_dict)

            # build sentiments dict
            sentiments_dict = {
                "tweet_score_afinn": score_afinn,
                "tweet_score_swn_pos": score_pos,
                "tweet_score_swn_neg": score_neg,
                "tweet_score_swn_obj": score_obj
            }
            sentiments_dict.update(pos_dict_mongo)

            ids_to_update = [tweet_id] + gen_peer_tweet_ids(tweet_id, tweet_links_dict, retweet_reverse_lookup_list)

            collection.update(
                {"_id": {"$in": ids_to_update}},
                {'$set': sentiments_dict},
                multi=True)

    def set_all_tweets_type(self):
        db = self.dbclient.get_db()

        # get tweet collection names
        collection_names = get_tweet_collections_only(db.collection_names())

        # iterate through all collections
        for collection_name in collection_names:
            self.set_all_tweet_type_collection(collection_name)

    def set_all_tweet_type_collection(self, collection_name):
        collection = self.dbclient.get_db()[collection_name]

        cursor = collection.find(
            {},
            {"_id": 1, 'retweeted_status': 1,
             'is_quote_status': 1, 'quoted_status_id': 1})

        for tweet in cursor:
            tweet_id = tweet['_id']
            tweet_type = get_tweet_type(tweet)

            collection.update(
                {"_id": tweet_id},
                {'$set': {"tweet_type": tweet_type}},
                multi=False)

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
