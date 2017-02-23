def db_tweets_to_tweets_dict(tweets_list):
    return {tweet['_id']: tweet for tweet in tweets_list}
