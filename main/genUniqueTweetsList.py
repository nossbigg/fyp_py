# Generates list of unique tweets and stores it into database
# TODO modularize this (so that can use with other collections)

import controller.DataMunger as DM
import model.TweetType as TT
import pymongo

# retrieve tweets from mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets
query = collection.find({}, {"id": 1, "tweet_type": 1, "retweeted_status": 1})

# create tweet dictionary
dataMunger = DM.DataMunger()
tweetList = list(query)
tweetDict = dataMunger.buildTweetDictFromList(tweetList)

# generate csv for labelling
# stores tweets that have already been represented (prevents duplicates of retweets with same parent)
tweets = {}
tweetParentToIdLookup = {}

for tweet in tweetDict.values():
  tweetId = tweet['id']
  # for retweets
  if tweet['tweet_type'] == TT.TweetType.RETWEET:
    parentTweetId = tweet['retweeted_status']['id']
    if parentTweetId not in tweetParentToIdLookup:
      tweetParentToIdLookup[parentTweetId] = tweetId
      tweets[tweetId] = []
    else:
      tweets[tweetParentToIdLookup[parentTweetId]].append(tweetId)
      continue
  # for all other types
  else:
    if tweetId not in tweets:
      tweets[tweetId] = []
    else:
      #FIXME algo when represented tweet meets parent
      pass

tweetListExport = []
for key, value in tweets.iteritems():
  obj = {
    "id": key,
    "related_tweets": value
  }
  tweetListExport.append(obj)

# write to db (also wipes db)
collection = db.sickhillaryDbUnique
collection.remove({})
collection.insert(tweetListExport)
client.close()
