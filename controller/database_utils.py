import os
import re

COLLECTION_NAME_LINKS_SUFFIX = "__parentlinks"
collection_name_links_pattern = re.compile("^.*" + COLLECTION_NAME_LINKS_SUFFIX + "$")


def get_collection_links_name_from_collection_name(collection_name):
    return collection_name + COLLECTION_NAME_LINKS_SUFFIX


def get_tweet_collections_only(collection_names):
    return [name for name in collection_names if not is_links_collection(name)]


def is_links_collection(collection_name):
    m = collection_name_links_pattern.match(collection_name)
    return m is not None


def get_collectionname_from_source_path(path):
    dbname = os.path.basename(path)
    dbname = re.sub('[ -]', '_', dbname)
    dbname = re.sub('[^a-zA-Z0-9_]', '', dbname)

    return dbname
