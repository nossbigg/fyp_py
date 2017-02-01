# update database with read labels
import pymongo
from afinn import Afinn

client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# query: get all tweets
query = collection.find({}, {"id": 1, "text": 1})
tweetList = list(query)

afinn = Afinn()

# save afinn scores
for tweet in tweetList:
  tweet_id = tweet['id']
  afinn_score = afinn.score(tweet['text'])

  result = db.tweets.update(
    {"id": tweet_id},
    {'$set': {"tweet_afinn_label": afinn_score}},
    multi=False
  )

# TODO parallelize afinn labelling process
