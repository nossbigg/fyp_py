# Technique 3: Keywords model
import nltk
import pandas as pd
import pymongo

# import tweets
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.tweets

query = collection.find({}, {"id": 1, "text": 1})
pdAll = pd.DataFrame(list(query))

pdAll['text'] = [text.encode("utf-8") for text in pdAll['text']]

# clean tweets
tweets = []
for (words) in pdAll['text']:
  words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
  tweets.append(words_filtered)

def get_words_in_tweets(tweets):
  all_words = []
  for (words) in tweets:
    all_words.extend(words)
  return all_words
def get_word_features(wordlist):
  wordlist = nltk.FreqDist(wordlist)
  word_features = wordlist.keys()
  return word_features
word_features = get_word_features(get_words_in_tweets(tweets))

print(word_features)

def extract_features(document):
  document_words = set(document)
  features = {}
  for word in word_features:
    features['contains(%s)' % word] = (word in document_words)
  return features
training_set = nltk.classify.apply_features(extract_features, tweets)

classifier = nltk.NaiveBayesClassifier.train(training_set)
