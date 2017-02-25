import model.tweet_type as TweetType

class TweetProcessingUtils:
  @staticmethod
  def labelTweetTypeByList(tweetDict):
    """
    Adds label to tweets in a list of tweets (in a dictionary)

    :param tweetDict:
    :return:
    """
    for tweetKey in tweetDict:
      tweet = tweetDict[tweetKey]
      tweet['tweet_type'] = TweetProcessingUtils.labelTweetType(tweet)
    return tweetDict

  @staticmethod
  def labelTweetType(tweet):
    """
    Determines the type of tweet given the tweet structure

    :param tweet:
    :return:
    """
    if 'retweeted_status' in tweet:
      return TweetType.TweetType.RETWEET
    elif tweet['is_quote_status'] is True:
      if 'quoted_status_id' in tweet:
        return TweetType.TweetType.QUOTE_RETWEET
      else:
        return TweetType.TweetType.INVALID
    else:
      return TweetType.TweetType.NORMAL

  @staticmethod
  def buildTweetDictFromList(tweetList):
    """
    Builds a dictionary of tweets based on a list of tweets

    :param tweetList:
    :return:
    """
    tweetDict = {}
    for tweet in tweetList:
      tweetDict[tweet['id']] = tweet
    return tweetDict

  @staticmethod
  def addTweetSentimentLabelToDict(tweetDict):
    for tweetKey in tweetDict:
      tweetDict[tweetKey]['tweet_sentiment_label'] = ''
    return tweetDict