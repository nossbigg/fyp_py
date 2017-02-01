import pymongo

client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets
db.tweets.update(
  { },
  {'$set': {"tweet_sentiment_label": ""}},
  multi=True
)

client.close()