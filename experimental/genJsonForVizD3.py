import controller.TweetProcessingUtils as TPU
import controller.graph_tweet_manager as GM
import pymongo

# retrieve tweets from mongo
from controller.graph_viz_utils import get_d3_data_format

client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# query: get all tweets
query = collection.find()

# create tweet dictionary
tweetList = list(query)
tweetDict = TPU.TweetProcessingUtils.buildTweetDictFromList(tweetList)


# method to generate json file
def genD3JsonFile(tweetDict, filename):
    # generate graph
    graphManager = GM.GraphManager(tweetDict)

    # generate and save graph to d3 format
    graph_data_d3 = get_d3_data_format(graphManager.get_graph())
    target = open(filename, 'w')
    target.write(graph_data_d3)
    target.close()


# save full d3
genD3JsonFile(tweetDict, "tweetD3(full).json")

# save partial d3
tweetDictN = {}
n = 1000
count = 0
for tweetKey in tweetDict:
    tweetDictN[tweetKey] = tweetDict[tweetKey]
    count += 1
    if not count < n:
        break
genD3JsonFile(tweetDictN, "tweetD3(" + str(n) + ").json")

# save full d3, but with nodes with at least n child
# TODO create graph, then find nodes with at least n child
degree = 0
# genD3JsonFile(tweetDict, "tweetD3(full)"+degree+".json",degree)
