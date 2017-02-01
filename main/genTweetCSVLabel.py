import csv

import pymongo

# retrieve tweets from mongo
client = pymongo.MongoClient()
db = client.tweetDb

# collection = db.tweets
#
# query: pick tweets that have not been labelled
# query = collection.find()
# query = collection.find({"tweet_sentiment_label": ""}).limit(200)

# create tweet dictionary
# dataMunger = DM.DataMunger()
# tweetList = list(query)
# tweetDict = dataMunger.buildTweetDictFromList(tweetList)

# generate graph
# graphManager = GM.GraphManager(tweetDict)
# missingTweetList = graphManager.getMissingTweets(tweetDict)

# generate csv for labelling
# stores tweets that have already been represented (prevents duplicates of retweets with same parent)
# tweetsRepresented = {}
# tweetDictExport = {}
# for tweet in tweetDict.values():
#   tweetId = tweet['id']
#   # for retweets
#   if tweet['tweet_type'] == TT.TweetType.RETWEET:
#     parentTweetId = tweet['retweeted_status']['id']
#     if parentTweetId not in tweetsRepresented:
#       tweetsRepresented[parentTweetId] = 0
#     else:
#       continue
#   # for all other types
#   else:
#     tweetsRepresented[tweetId] = 0
#   tweetDictExport[tweet['id']] = tweet


# get list of unique tweets to retrieve
collection = db.sickhillaryDbUnique
uniqueTweetList = list(collection.find({}))

tweetDict = {}
for tweet in uniqueTweetList:
  tweetDict[tweet['id']] = tweet['related_tweets']

# sort by number of related tweets (descending)
sortIdDesc = sorted(tweetDict, key=lambda k: len(tweetDict[k]), reverse=True)
# sortIdDesc = [long(id) for id in sortIdDesc]

# build tweet list to export
collection = db.tweets
query = collection.find({"id": {"$in": sortIdDesc}})
retrievedTweets = {}
for doc in query:
  retrievedTweets[doc['id']] = doc

# write to csv
with open('tweetsToLabel.csv', 'wb') as csvfile:
  writer = csv.writer(csvfile, delimiter='|')
  writer.writerow(['count', 'type', 'text', 'id', 'tweet_type'])
  count = 1
  for id in sortIdDesc:
    tweet = retrievedTweets[id]
    writer.writerow([count, '', tweet['text'].encode('utf-8').replace("\n", "")
                      , tweet['id'], tweet['tweet_type']])
    count += 1
