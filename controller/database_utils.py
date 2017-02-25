import os
import re

COLLECTION_NAME_LINKS_SUFFIX = "__parentlinks"
collection_name_links_pattern = re.compile("^.*" + COLLECTION_NAME_LINKS_SUFFIX + "$")


def get_collection_links_name_from_collection_name(collection_name):
    return collection_name + COLLECTION_NAME_LINKS_SUFFIX


def get_tweet_collections_only(collection_names):
    return [name for name in collection_names if not is_links_collection(name)]


def get_tweet_collections_links_only(collection_names):
    return [name for name in collection_names if is_links_collection(name)]


def is_links_collection(collection_name):
    m = collection_name_links_pattern.match(collection_name)
    return m is not None


def get_collectionname_from_source_path(path):
    dbname = os.path.basename(path)
    dbname = re.sub('[ -]', '_', dbname)
    dbname = re.sub('[^a-zA-Z0-9_]', '', dbname)

    return dbname


def gen_unique_tweet_ids_from_links(tweet_links, sorted_by_childs_length=False):
    if sorted_by_childs_length:
        tweet_links.sort(key=lambda tl: len(tl['childs']), reverse=True)

    unique_tweet_list = []
    for doc in tweet_links:
        if doc['represented_by_id'] is None:
            unique_tweet_list.append(doc['_id'])
        else:
            unique_tweet_list.append(doc['represented_by_id'])

    unique_tweet_list = [long(tweet_id) for tweet_id in unique_tweet_list]

    return unique_tweet_list
