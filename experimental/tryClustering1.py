# Technique 2
# Unsupervised clustering
import pandas as pd
import pymongo
from matplotlib import pyplot as plt
from nltk import PorterStemmer, FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from scipy.cluster.hierarchy import linkage, dendrogram

client = pymongo.MongoClient()
db = client.tweetDb

# get list of unique tweets to retrieve
collection = db.sickhillaryDbUnique
uniqueTweetList = list(collection.find({}))
uniqueTweetList = [long(v["id"]) for v in uniqueTweetList]

# get tweets
collection = db.tweets
query = collection.find(
  {"id": {"$in": uniqueTweetList}},
  {"id": 1, "text": 1}).limit(1000)
pdAll = pd.DataFrame(list(query))

# tokenize
tknzr = TweetTokenizer(preserve_case=True,
                       reduce_len=False, strip_handles=False)
pdAll['original_tokens'] = [tknzr.tokenize(text) for text in pdAll['text']]

twt = {}
for index, row in pdAll.iterrows():
  twt[row["id"]] = row['original_tokens']

# TODO remove http, # and @ (use regex)

# remove stopwords
stopwordlist = stopwords.words('english')
for id in twt:
  tokens = twt[id]
  filtered = [w for w in tokens if not w in stopwordlist]
  twt[id] = filtered

# remove custom word list
# customwordlist = []
# for id in twt:
#   tokens = twt[id]
#   filtered = [w for w in tokens if not w in customwordlist]
#   twt[id] = filtered

# lemmatize tokens
stemmer = PorterStemmer()
for id in twt:
  tokens = twt[id]
  twt[id] = [stemmer.stem(w) for w in tokens]

# remove words that are below 3 characters
for id in twt:
  tokens = twt[id]
  twt[id] = [w for w in tokens if len(w) > 3]

# generate term frequencies per tweet
totalFreq = FreqDist([item for sublist in twt.values() for item in sublist])

freqs = totalFreq.values()
# 3 std dev over and under
upperQ = pd.np.percentile(freqs, 99.73)
lowerQ = pd.np.percentile(freqs, 0.27)
termsSelected = [term for term in totalFreq if upperQ > totalFreq[term] > lowerQ]

termsFreq = []
for id in twt:
  freqDistTemp = FreqDist(twt[id])
  termFreqTwt = []
  for term in termsSelected:
    if term in freqDistTemp:
      termFreqTwt.append(freqDistTemp[term])
    else:
      termFreqTwt.append(0)
  termFreqTwt = [float(v) for v in termFreqTwt]
  termsFreq.append(termFreqTwt)
pdAll['term_freq'] = termsFreq

# generate term frequency (binary)
termsFreqBinary = []
for list in termsFreq:
  tempList = []
  for freq in list:
    if freq > 0:
      tempList.append(1)
    else:
      tempList.append(0)
  termsFreqBinary.append(tempList)
pdAll['term_freq_bin'] = termsFreqBinary

# hierarchical clustering
# TODO can consider using cuda for k-means (via tensorflow)
# convert pd to ndarray format
ndarrTemp = pd.np.array(pdAll['term_freq_bin'].values.tolist())
Z = linkage(ndarrTemp, method='ward')

# calculate full dendrogram
plt.figure(figsize=(25, 10))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
dendrogram(
  Z,
  leaf_rotation=90.,  # rotates the x axis labels
  leaf_font_size=8.,  # font size for the x axis labels
)
plt.show()
