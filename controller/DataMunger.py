import glob
import gzip
import json

import model.TweetType as TT


class DataMunger:
  def getTweetsFromSource(self, dirToSearch):
    """
    Retrieves gzipped tweet archives and imports them into a dictionary

    :param dirToSearch:
    :return:
    """
    tweetsJsonDict = {}

    # read from local files
    filesListPath = glob.glob(dirToSearch + "/*.gz")
    requestListJson = []
    for filePath in filesListPath:
      with gzip.open(filePath, 'r') as fin:
        for line in fin:
          l = line.decode("utf-8")
          l = l.strip()
          j = json.loads(l)
          requestListJson.append(j)

          # gzipFile = gzip.open(filePath)
          # content = str(gzipFile.read())
          # content = content[2:]
          # content = content[:-1]
          # filesListJSON.append(content)
          # break

    # get unique tweets
    collisions = 0
    count = 0
    for requestJson in requestListJson:
      tweets = requestJson["statuses"]
      for tweet in tweets:
        count += 1
        id = tweet["id"]
        if id not in tweetsJsonDict:
          tweetsJsonDict[id] = tweet
        else:
          collisions += 1

    return tweetsJsonDict

  def labelTweetTypeByList(self, tweetDict):
    """
    Adds label to tweets in a list of tweets (in a dictionary)

    :param tweetDict:
    :return:
    """
    for tweetKey in tweetDict:
      tweet = tweetDict[tweetKey]
      tweet['tweet_type'] = self.labelTweetType(tweet)
    return tweetDict

  def labelTweetType(self, tweet):
    """
    Determines the type of tweet given the tweet structure

    :param tweet:
    :return:
    """
    if 'retweeted_status' in tweet:
      return TT.TweetType.RETWEET
    elif tweet['is_quote_status'] is True:
      if 'quoted_status_id' in tweet:
        return TT.TweetType.QUOTE_RETWEET
      else:
        return TT.TweetType.INVALID
    else:
      return TT.TweetType.NORMAL

  def buildTweetDictFromList(self, tweetList):
    """
    Builds a dictionary of tweets based on a list of tweets

    :param tweetList:
    :return:
    """
    tweetDict = {}
    for tweet in tweetList:
      tweetDict[tweet['id']] = tweet
    return tweetDict

  def addTweetSentimentLabelToDict(self, tweetDict):
    for tweetKey in tweetDict:
      tweetDict[tweetKey]['tweet_sentiment_label'] = ''
    return tweetDict
