# Imports unique tweets from source files into mongodb

import pymongo
from controller import TweetProcessingUtils as TPU
from test import DataMunger as DM

dirToSearch = "C:/Users/Gibson/adbpull/com.nossbigg.htmlminder/files/data/gib-tweet-fyp/#sickhillary"
dataMunger = DM.DataMunger()
tweetsDict = dataMunger.getTweetsFromSource(dirToSearch)

# label tweets by type
tweetsDict = TPU.TweetProcessingUtils.labelTweetTypeByList(tweetsDict)
# add sentiment label field
tweetsDict = TPU.TweetProcessingUtils.addTweetSentimentLabelToDict(tweetsDict)
# convert time fields into timestamp
# TODO convert time fields to mongodb timestamp

# print(len(tweetsDict))

# save to mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets
result = collection.insert(list(tweetsDict.values()))
client.close()
