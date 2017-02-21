import pandas as pd
import pymongo
from controller import PreprocessingUtils as PPU
from controller.MLUtils import MLUtils
from controller.NLTKManager import NLTKManager as NLTKMgr
from sklearn import svm, tree, ensemble, naive_bayes, linear_model, neural_network
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split

nltkMgr = NLTKMgr()

# get unique tweets which are sentiment-labelled
client = pymongo.MongoClient()
db = client.tweetDb
collection = db.sickhillaryDbUnique
uniqueTweetList = list(collection.find({}, {"id": 1}))
uniqueTweetList = [item["id"] for item in uniqueTweetList]

collection = db.tweets
query = collection.find(
  {"id": {"$in": uniqueTweetList},
   "tweet_sentiment_label": {"$ne": ""}},
  {"id": 1, "text": 1, "tweet_sentiment_label": 1})

# create dataframe
pdAll = pd.DataFrame(list(query))

# create copy
text_tokens = [nltkMgr.tokenize(text) for text in pdAll['text']]
pdAll['original_tokens'] = text_tokens

# text preprocessing
text_tokens = [PPU.PreprocessingUtils.removeTokenHTTP(tokens) for tokens in text_tokens]
text_tokens = [PPU.PreprocessingUtils.removeTokenUserReference(tokens) for tokens in text_tokens]
text_tokens = [PPU.PreprocessingUtils.removeTokenHashtag(tokens) for tokens in text_tokens]
text_tokens = [nltkMgr.removeStopwordTokens(tokens) for tokens in text_tokens]
text_tokens = [nltkMgr.lemmatizeTokens(tokens) for tokens in text_tokens]
text_tokens = [PPU.PreprocessingUtils.removeTokenByLength(tokens, 3, 999) for tokens in text_tokens]

# gen global term frequencies
totalFreq = nltkMgr.genFreqDist([item for sublist in text_tokens for item in sublist])
termsSelected = PPU.PreprocessingUtils.getTermsWithinStdDev(totalFreq, 3, 3)
totalFreq.values()

tokens_vec = [nltkMgr.genFreqVector(tokens, termsSelected) for tokens in text_tokens]
tokens_vec_bin = [nltkMgr.genFreqVector(tokens, termsSelected, True) for tokens in text_tokens]

# store terms
pdAll['ml_vec'] = tokens_vec
pdAll['ml_vec_bin'] = tokens_vec_bin

# prep dataset
df = pdAll
df["tweet_sentiment_label2"] = [1 if row['tweet_sentiment_label'] == "s" else 0 for index, row in df.iterrows()]
train, test = train_test_split(df, test_size=0.2)

train_feature = pd.np.array(train["ml_vec_bin"].tolist())
train_label = pd.np.array(train["tweet_sentiment_label2"].tolist())
test_feature = pd.np.array(test["ml_vec_bin"].tolist())
test_label = pd.np.array(test["tweet_sentiment_label2"].tolist())

# ML
# Support Vector Machine
acc = MLUtils.testML(svm.SVC(),
                     train_feature, train_label, test_feature, test_label)
print("SVM accuracy: " + acc)
# Decision Trees
acc = MLUtils.testML(tree.DecisionTreeClassifier(),
                     train_feature, train_label, test_feature, test_label)
print("DT accuracy: " + acc)
# Logistic Regression
acc = MLUtils.testML(linear_model.LogisticRegression(),
                     train_feature, train_label, test_feature, test_label)
print("LR accuracy: " + acc)
# Naive Bayes (Bernoulli)
acc = MLUtils.testML(naive_bayes.BernoulliNB(),
                     train_feature, train_label, test_feature, test_label)
print("NB (Bernoulli) accuracy: " + acc)
# Random Forests
acc = MLUtils.testML(ensemble.RandomForestClassifier(),
                     train_feature, train_label, test_feature, test_label)
print("RFR accuracy: " + acc)
# Gradient Boosted Trees
acc = MLUtils.testML(ensemble.GradientBoostingClassifier(),
                     train_feature, train_label, test_feature, test_label)
print("GRB accuracy: " + acc)

# Neural Network

acc = MLUtils.testML(neural_network.MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(15,), random_state=1),
                     train_feature, train_label, test_feature, test_label)
print("NN accuracy: " + acc)

# LDA
# http://scikit-learn.org/stable/auto_examples/applications/topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-topics-extraction-with-nmf-lda-py
n_samples = 2000
n_features = 1000
n_topics = 10
n_top_words = 20

data_samples = pdAll['text'][:n_samples]

tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                   max_features=n_features,
                                   stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(data_samples)

tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                max_features=n_features,
                                stop_words='english')
tf = tf_vectorizer.fit_transform(data_samples)


tfidf_feature_names = tfidf_vectorizer.get_feature_names()

lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)
lda.fit(tf)

def print_top_words(model, feature_names, n_top_words):
  for topic_idx, topic in enumerate(model.components_):
    print("Topic #%d:" % topic_idx)
    print(" ".join([feature_names[i]
                    for i in topic.argsort()[:-n_top_words - 1:-1]]))
  print()

print("\nTopics in LDA model:")
tf_feature_names = tf_vectorizer.get_feature_names()
print_top_words(lda, tf_feature_names, n_top_words)

# TODO use tf-idf to retain valuable but sparse terms
# TODO use k-fold cv with stratification -> http://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data
# TODO use k-means with elbow method

pass
