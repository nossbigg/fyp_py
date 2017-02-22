import TweetType
import networkx as nx


class GraphManager:
    __graph = nx.Graph()
    __tweets_dict = {}

    def __init__(self, tweets_dict):
        self.__tweets_dict = tweets_dict
        self.__graph = self.__gen_graph_from_tweet_dict(tweets_dict)

    def get_graph(self):
        return self.__graph

    def get_tweets(self):
        return self.__tweets_dict

    @staticmethod
    def __gen_graph_from_tweet_dict(tweets_dict):
        """
        Builds graph from given dictionary of tweets

        :param tweets_dict:
        :return:
        """
        g = nx.Graph()

        for tweetKey in tweets_dict:
            tweet = tweets_dict[tweetKey]
            tweet_id = tweet['id']
            g.add_node(tweet_id)
            tweet_id_parent = -1

            tweet_type_enum = tweet['tweet_type']

            if tweet_type_enum == TweetType.RETWEET:
                tweet_id_parent = tweet['retweeted_status']['id']
            elif tweet_type_enum == TweetType.QUOTE_RETWEET:
                tweet_id_parent = tweet['quoted_status_id']

            if tweet_id_parent != -1:
                g.add_edge(tweet_id, tweet_id_parent)

        return g

    def get_missing_tweets(self):
        """
        Gets tweets that are not represented in the dictionary
    -
        :return:
        """
        missing_tweets = []

        for tweetId in self.__graph.nodes():
            if tweetId not in self.__tweets_dict:
                missing_tweets.append(tweetId)

        return missing_tweets

    def getUniqueParentTweets(self):
        # TODO
        return 1
