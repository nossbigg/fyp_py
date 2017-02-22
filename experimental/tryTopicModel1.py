# Technique 1: Topic Modeling
# ref: http://d10genes.github.io/blog/2013/07/04/nyt-nlp/

import pandas as pd
import pymongo
from gensim import corpora
from gensim import models
from gensim import similarities

from nltk.corpus import sentiwordnet as swn

# SA

# import tweets
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

query = collection.find({}, {"id": 1, "text": 1})
pdAll = pd.DataFrame(list(query))

# remove stopwords


# lemmatize words

dmap = lambda dct, a: [dct[e] for e in a]

texts = pdAll['text']
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]
tdidf = models.TfidfModel(corpus)
tcorpus = dmap(tdidf,corpus)

model = models.lsimodel.LsiModel(corpus=tcorpus, id2word=dictionary, num_topics=15)

# VIZ

# generate wordcloud (py)




# ML
