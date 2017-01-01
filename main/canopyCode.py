import pymongo, networkx as nx, matplotlib.pyplot as plt

# retrieve tweets from mongo
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

tweets = list(collection.find())
# tweets = list(collection.find().limit(20))

client.close()

# build graph
g = nx.Graph()
node_colors = []

for tweet in tweets:
  id = tweet['id']
  g.add_node(id)

  parentTweetId = -1
  if 'retweeted_status' in tweet:
    parentTweetId = tweet['retweeted_status']['id']
    node_colors.append(1)
  elif tweet['is_quote_status'] is True:
    if 'quoted_status_id' in tweet:
      parentTweetId = tweet['quoted_status_id']
    node_colors.append(2)
  else:
    node_colors.append(3)

  if parentTweetId != -1:
    g.add_edge(id, parentTweetId)

# plot graph
nx.draw(g)
# nx.draw(g, cmap=plt.get_cmap('jet'), node_colors=node_colors)
plt.show()
# http://stackoverflow.com/questions/20133479/how-to-draw-directed-graphs-using-networkx-in-python
