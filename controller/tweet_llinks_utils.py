from TweetType import TweetType
from tweet_link import TweetLink


def generate_links_dict(tweets_dict):
    """
    Generates a dictionary that maps parent->child retweet relationship of tweets.
    This data structure is used to propagate sentiment labels from parent->child.
    Quote-retweets will not be mapped to their parents, as they contain their own textual information.

    Algorithm
    ---------
    Scenario A:
    If tweet is normal tweet, enter as parent
    Scenario B:
    If tweet is retweet and parent exists, enter as child to parent
    Scenario C:
    If tweet is retweet and parent does not exist, enter as parent,
        and add mapping of itself to original id to *represented*
    Scenario D:
    If tweet is normal tweet and there is existing parent->child mapping,
        Replace mapping, making normal tweet as parent, and appending previous parent as child
    (note: quote retweets also constitute as normal tweets, as far as this algo goes)

    :param tweets_dict:
    :return:
    """
    links_dict = {}

    for tweet in tweets_dict.values():
        tweet_id = tweet['id']
        tweet_type = tweet['tweet_type']

        if tweet_type == TweetType.RETWEET:
            tweet_id_parent = tweet['retweeted_status']['id']
            # Scenario C
            if tweet_id_parent not in links_dict:
                tl = TweetLink(tweet_id_parent, tweet_id)
                tl.childs.append(tweet_id)
                links_dict[tweet_id_parent] = tl
            # Scenario B
            else:
                links_dict[tweet_id_parent].childs.append(tweet_id)

        elif tweet_type == TweetType.NORMAL or tweet_type == TweetType.QUOTE_RETWEET:
            # Scenario A
            if tweet_id not in links_dict:
                tl = TweetLink(tweet_id)
                links_dict[tweet_id] = tl
            # Scenario D
            else:
                existing_tl = links_dict[tweet_id]
                existing_tl.childs.append(existing_tl.represented_by_id)
                existing_tl.represented_by_id = None
                links_dict[tweet_id] = existing_tl

    return links_dict


def links_dict_to_mongo(links_dict):
    mongo_items = []

    for tweet_id, tl in links_dict.iteritems():
        tl_dict = vars(tl)
        tl_dict["_id"] = tl_dict["id"]
        del tl_dict["id"]
        mongo_items.append(tl_dict)

    return mongo_items
