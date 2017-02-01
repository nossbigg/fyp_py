import nltk
import pymongo
from nltk.corpus import sentiwordnet as swn

# http://www.nltk.org/_modules/nltk/corpus/reader/sentiwordnet.html

# update database with read labels
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

# query: get all tweets
query = collection.find({}, {"id": 1, "text": 1})
tweetList = list(query)

tknzr = nltk.TweetTokenizer(preserve_case=False,
                            reduce_len=False, strip_handles=False)

# generate and save swn of tweet
for tweet in tweetList:
  tweet_id = tweet['id']

  tokens = tknzr.tokenize(tweet['text'])

  pos_scores = 0.0
  neg_scores = 0.0
  obj_scores = 0.0

  for token in tokens:
    matchedWords = list(swn.senti_synsets(token))
    if len(matchedWords) == 0: continue

    sentiment = matchedWords[0]
    pos_scores += sentiment.pos_score()
    neg_scores += sentiment.neg_score()
    obj_scores += sentiment.obj_score()

  pos_scores /= len(tokens)
  neg_scores /= len(tokens)
  obj_scores /= len(tokens)

  result = db.tweets.update(
    {"id": tweet_id},
    {'$set': {
      "tweet_swn_pos_score": pos_scores,
      "tweet_swn_neg_score": neg_scores,
      "tweet_swn_obj_score": obj_scores
    }},
    multi=False
  )

# TODO possible to improve with POS tagging
