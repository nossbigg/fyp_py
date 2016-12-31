import pymongo

# save to mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# tweets = list(collection.find())
tweets = list(collection.find().limit(20))

# tweets = []
# for tweet in collection.find().batch_size(50000):
#   tweets.append(tweet)

print(tweets[0])

# for tweet in tweets:


client.close()
