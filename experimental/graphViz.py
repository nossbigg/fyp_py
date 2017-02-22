import controller.graph_tweet_manager as GM
import controller.graph_viz_utils as GV
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
G = graphManager.get_graph()
degree_values = nx.degree(G).values()

# generate graph degree histogram
GV.gen_plt_degree_dist(graphManager.get_graph())
