# Imports unique tweets from source files into mongodb

import os, pymongo
from controller import DataMunger as DM

# get unique tweets from source
dirToSearch = "C:\\Users\\Gibson\\adbpull\\data\\gib-tweet-fyp\\#sickhillary"
DataMunger = DM.DataMunger(os.getcwd())
tweetsJsonList = DataMunger.getTweetsFromSource(dirToSearch)

print(len(tweetsJsonList))

# save to mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets
result = collection.insert_many(list(tweetsJsonList.values()))
client.close()