import controller.DataMunger as DM
import controller.GraphManager as GM
import controller.GraphVizUtils as GV
import networkx as nx
import pymongo

# retrieve tweets from mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# query: get all tweets
query = collection.find()

# create tweet dictionary
dataMunger = DM.DataMunger()
tweetList = list(query)
tweetDict = dataMunger.buildTweetDictFromList(tweetList)

# generate graph
graphManager = GM.GraphManager(tweetDict)

# test
G = graphManager.graph
degree_values = nx.degree(G).values()

# generate graph degree histogram
gv = GV.GraphVizUtils()
gv.displayGraphDegreeDist(graphManager.graph)

