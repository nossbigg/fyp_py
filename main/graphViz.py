import controller.GraphManager as GM
import controller.GraphVizUtils as GV
import networkx as nx
import pymongo

# retrieve tweets from mongo
from controller import TweetProcessingUtils as TPU

client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# query: get all tweets
query = collection.find().limit(100)

# create tweet dictionary
tweetList = list(query)
tweetDict = TPU.TweetProcessingUtils.buildTweetDictFromList(tweetList)

# generate graph
graphManager = GM.GraphManager(tweetDict)

# test
G = graphManager.graph
degree_values = nx.degree(G).values()

# generate graph degree histogram
gv = GV.GraphVizUtils()
gv.displayGraphDegreeDist(graphManager.graph)
