from datetime import datetime

import model.tweet_sentiment_label as TSL
import pymongo
import pytz
import pandas as pd

# retrieve tweets from mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# get max and min date
query = collection.find({}, {"created_at": 1})
tweets = list(query)
tweetTimeList = []
for tweet in tweets:
  # Fri Oct 28 03:20:56 +0000 2016
  # https://docs.python.org/2/library/datetime.html
  dt = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)
  tweetTimeList.append(dt)
tweetTimeList.sort()
minTime = tweetTimeList[0]
maxTime = tweetTimeList[-1]

print("First Tweet Time: " + minTime.strftime("%B %d, %Y"))
print("Last Tweet Time: " + maxTime.strftime("%B %d, %Y"))

# get all tweets
# pdAll = pd.DataFrame(list(collection.find()))


# get rumor support tweets
pdSupport = pd.DataFrame(list(collection.find(
  {"tweet_sentiment_label": TSL.TweetSentimentLabel.SUPPORT.value})))

# query = collection.find({"tweet_sentiment_label": TSL.TweetSentimentLabel.SUPPORT.value})
# tweetsSupportList = list(query)

# get rumor deny tweets
pdDeny = pd.DataFrame(list(collection.find(
  {"tweet_sentiment_label": TSL.TweetSentimentLabel.DENY.value})))

# query = collection.find({"tweet_sentiment_label": TSL.TweetSentimentLabel.DENY.value})
# tweetsDenyList = list(query)

print(pdSupport.head())
print(pdDeny.head())

# http://www.laurentluce.com/posts/twitter-sentiment-analysis-using-python-and-nltk/
# https://www.codementor.io/python/tutorial/data-science-python-r-sentiment-classification-machine-learning


# Latent Semantic Analysis ()
# http://blog.josephwilk.net/projects/latent-semantic-analysis-in-python.html

# topic modeling
# vocab distribution
# look out for emotions
