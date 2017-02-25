import model.tweet_type as TT
import model.tweet_sentiment_label as TSL

import pymongo

tweetsCsv = {}

filename = "tweetsToLabel labelled.csv"
with open(filename, 'rb') as f:
  count = 0
  for line in f:
    line = line.strip()

    # skip header row
    if count == 0:
      count += 1
      continue

    # skip empty lines
    if len(line) == 0:
      continue

    rowData = line.split('|')

    # skip empty sentiment
    if len(rowData[1]) == 0:
      continue

    tweet = {}
    tweet['id'] = int(rowData[3])
    tweet['tweet_sentiment_label'] = TSL.TweetSentimentLabel(rowData[1])
    tweetsCsv[tweet['id']] = tweet

    count += 1

# update database with read labels
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

for tweet in tweetsCsv.values():
  # retrieve tweet from db
  query = collection.find({"id": tweet['id']}).limit(1)
  tweetList = list(query)

  # skip tweet if no matches
  if len(tweetList) == 0:
    continue

  retrievedTweet = tweetList[0]
  retrievedTweetType = retrievedTweet['tweet_type']

  # if tweet is QUOTE or NORMAL, update tweet
  if retrievedTweetType == TT.TweetType.NORMAL or retrievedTweetType == TT.TweetType.QUOTE_RETWEET:
    result = db.tweets.update(
      {"id": tweet['id']},
      {'$set': {"tweet_sentiment_label": tweet['tweet_sentiment_label'].value}},
      multi=False
    )

  # if tweet is RETWEET, get parent id and update all child tweets
  elif retrievedTweetType == TT.TweetType.RETWEET:
    parentTweetId = retrievedTweet['retweeted_status']['id']
    result = db.tweets.update(
      {"retweeted_status.id": parentTweetId},
      {'$set': {"tweet_sentiment_label": tweet['tweet_sentiment_label'].value}},
      multi=True
    )

  else:
    # anomalous tweet of unknown type
    pass

client.close()
