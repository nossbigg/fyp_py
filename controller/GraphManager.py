import json

import model.TweetType as TT
import networkx as nx


class GraphManager:
  graph = nx.Graph()

  def __init__(self,tweetDict):
    self.graph = self.buildGraph(tweetDict)

  def buildGraph(self,tweetDict):
    """
    Builds graph from given dictionary of tweets

    :param tweetDict:
    :return:
    """
    g = nx.Graph()

    for tweetKey in tweetDict:
      tweet = tweetDict[tweetKey]
      id = tweet['id']
      g.add_node(id)
      parentTweetId = -1

      tweetTypeEnum = tweet['tweet_type']

      if tweetTypeEnum == TT.TweetType.RETWEET:
        parentTweetId = tweet['retweeted_status']['id']
      elif tweetTypeEnum == TT.TweetType.QUOTE_RETWEET:
        parentTweetId = tweet['quoted_status_id']

      if parentTweetId != -1:
        g.add_edge(id, parentTweetId)

    return g

  def getMissingTweets(self, tweetDict):
    """
    Gets tweets that are not represented in the dictionary
-
    :return:
    """
    missingTweetList = []

    for tweetId in self.graph.nodes():
      if tweetId not in tweetDict:
        missingTweetList.append(tweetId)

    return missingTweetList

  def getUniqueParentTweets(self):
    #TODO
    return 1

  def getD3VizJsonFormat(self):
    #ref: http://bl.ocks.org/mbostock/4062045
    returnDict = {}

    nodes = []
    for node in self.graph.nodes():
      d = {}
      d['id'] = node
      d['group'] = 1
      nodes.append(d)

    edges = []
    for edge in self.graph.edges():
      d = {}
      d['source'] = edge[0]
      d['target'] = edge[1]
      d['value'] = 1
      edges.append(d)

    returnDict["nodes"] = nodes
    returnDict["links"] = edges

    return json.dumps(returnDict,indent=2)
