def db_tweets_to_tweets_dict(tweets_list):
    return {long(tweet['_id']): tweet for tweet in tweets_list}
