import glob
import gzip
import os
import json


def get_archives_from_path(path):
    file_types = ['gz', 'text']
    archives = []
    for file_type in file_types:
        archives.extend(glob.glob(path + "/*." + file_type))
    return archives


def get_json_from_gzip_file(file_path):
    data = []
    with gzip.open(file_path, 'r') as fin:
        for line in fin:
            l = line.decode("utf-8")
            l = l.strip()
            json_data = json.loads(l)
            data.append(json_data)
    return data


def get_json_from_text_file(file_path):
    data = []
    with open(file_path, "r") as fin:
        for line in fin:
            l = line.decode("utf-8")
            l = l.strip()
            json_data = json.loads(l)
            data.append(json_data)
    return data


def get_json_from_archive_file(file_path):
    file_name, file_extension = os.path.splitext(file_path)
    file_extension = file_extension[1:]

    if file_extension == "gz" or file_extension == "gzip":
        return get_json_from_gzip_file(file_path)
    elif file_extension == "text" or file_extension == "txt":
        return get_json_from_text_file(file_path)


def get_tweets_from_archives(archives_json):
    tweets = {}
    for archive_json in archives_json:
        tweets_archive = get_tweets_from_archive(archive_json)
        for tweet in tweets_archive:
            tweet_id = tweet["id"]
            tweet["_id"] = tweet["id"]

            # prevents duplicates
            if tweet_id not in tweets:
                tweets[tweet_id] = tweet
    return tweets


def get_tweets_from_archive(archive_json):
    return archive_json["statuses"]


def convert_tweets_date(tweets):
    #FIXME replacing dict items in iteration is unstable
    for id, tweet in tweets.iteritems():
        tweet["created_at"] = tweet_date_to_mongodb_date(tweet["created_at"])
        tweets[id] = tweet
    return tweets


def tweet_date_to_mongodb_date(tweet_date):
    return tweet_date
    # TODO implement date conversion
