from model.tweet_type import TweetType
from model.tweet_link import TweetLink


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
        mongo_items.append(tl.to_mongo_item())

    return mongo_items


def gen_peer_tweet_ids(tweet_id, tweet_links_dict, retweet_reverse_lookup_list=None):
    """
    Generate a list of tweet ids to update, given an tweet_id.
    Scenario A: If tweet is parent, update all childs
    Scenario B: If tweet represents as parent, update all peers
    Scenario C: If tweet is one of peers, update parent and other peers (Unimplemented)

    :return:
    """
    if retweet_reverse_lookup_list is None:
        retweet_reverse_lookup_list = gen_represented_by_reverse_lookup_dict(tweet_links_dict)

    ids_to_update = []
    lookup_id = None

    # Scenario A
    if tweet_id in tweet_links_dict:
        lookup_id = tweet_id
    # Scenario B
    elif tweet_id in retweet_reverse_lookup_list:
        lookup_id = retweet_reverse_lookup_list[tweet_id]

    if lookup_id is not None:
        childs = tweet_links_dict[lookup_id]["childs"]
        ids_to_update += childs

    return ids_to_update


def gen_tweet_links_dict(tweet_links_list):
    return {l["_id"]: l for l in tweet_links_list}


def gen_represented_by_reverse_lookup_dict(links):
    return {l["represented_by_id"]: l["_id"] for l in links
            if l["represented_by_id"] is not None}
