# Imports unique tweets from source files into mongodb

import pymongo
from controller import DataMunger as DM

# get unique tweets from source
dirToSearch = "C:\\Users\\Gibson\\adbpull\\data\\gib-tweet-fyp\\#sickhillary"
dataMunger = DM.DataMunger()
tweetsDict = dataMunger.getTweetsFromSource(dirToSearch)

# label tweets by type
tweetsDict = dataMunger.labelTweetTypeByList(tweetsDict)
# add sentiment label field
tweetsDict = dataMunger.addTweetSentimentLabelToDict(tweetsDict)
# convert time fields into timestamp
# TODO convert time fields to mongodb timestamp

# print(len(tweetsDict))

# save to mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets
result = collection.insert(list(tweetsDict.values()))
client.close()
