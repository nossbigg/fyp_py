import csv
import itertools

import pandas as pd
import pymongo
from controller import preprocessing_utils as PPU
from controller.ml_utils import MLUtils
from controller.nltk_manager import NLTKManager as NLTKMgr
from sklearn import preprocessing
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

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
    {"id": 1, "text": 1, "tweet_sentiment_label": 1,
     "tweet_afinn_label": 1, "tweet_swn_neg_score": 1,
     "tweet_swn_obj_score": 1, "tweet_swn_pos_score": 1})

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

tokens_vec = [nltkMgr.genFreqVector(tokens, termsSelected) for tokens in text_tokens]
tokens_vec_bin = [nltkMgr.genFreqVector(tokens, termsSelected, True) for tokens in text_tokens]

# normalize tokens_vec
minNum = 0
maxNum = -1
for tokens_vec_sublist in tokens_vec:
    for count in tokens_vec_sublist:
        if count > maxNum:
            maxNum = count
        elif count < minNum:
            minNum = count
min_max_scaler = preprocessing.MinMaxScaler(feature_range=(minNum, maxNum), copy=True)
tokens_vec = [min_max_scaler.fit_transform(v) for v in tokens_vec]

# append useful features
min_max_scaler_2 = preprocessing.MinMaxScaler()
pdAll['tweet_afinn_label'] = min_max_scaler_2.fit_transform(pdAll['tweet_afinn_label'])
pdAll['tweet_swn_neg_score'] = min_max_scaler_2.fit_transform(pdAll['tweet_swn_neg_score'])
pdAll['tweet_swn_obj_score'] = min_max_scaler_2.fit_transform(pdAll['tweet_swn_obj_score'])
pdAll['tweet_swn_pos_score'] = min_max_scaler_2.fit_transform(pdAll['tweet_swn_pos_score'])

tokens_vec = [vec + [a] + [b] + [c] + [d] for vec, a, b, c, d
              in itertools.izip(tokens_vec,
                                pdAll['tweet_afinn_label'].tolist(),
                                pdAll['tweet_swn_neg_score'].tolist(),
                                pdAll['tweet_swn_obj_score'].tolist(),
                                pdAll['tweet_swn_pos_score'].tolist())]

tokens_vec_bin = [vec + [a] + [b] + [c] + [d] for vec, a, b, c, d
                  in itertools.izip(tokens_vec_bin,
                                    pdAll['tweet_afinn_label'].tolist(),
                                    pdAll['tweet_swn_neg_score'].tolist(),
                                    pdAll['tweet_swn_obj_score'].tolist(),
                                    pdAll['tweet_swn_pos_score'].tolist())]

# store terms
pdAll['ml_vec'] = tokens_vec
pdAll['ml_vec_bin'] = tokens_vec_bin

# prep dataset
df = pdAll
df["tweet_sentiment_label2"] = [1 if row['tweet_sentiment_label'] == "s" else 0 for index, row in df.iterrows()]

# ML
ml_list = {
    "SVM": MLUtils.clfSVC,
    "DT": MLUtils.clfDT,
    "LR": MLUtils.clfLR,
    "NBBernoulli": MLUtils.clfNBBernoulli,
    "NBMulti": MLUtils.clfNBMultinomial,
    "RFR": MLUtils.clfRFR,
    "GRB": MLUtils.clfGRB,
    "NN": MLUtils.clfNN
}

acc_list = MLUtils.testMultipleMLWithIter(ml_list, 30, df)

with open('ml_test_keyword.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    ml_keys_alphabetical = sorted(ml_list.keys())

    writer.writerow(ml_keys_alphabetical)
    for acc_sublist in acc_list:
        writer.writerow(acc_sublist)

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
# TODO investigate pipelining (see if it helps with anything)



pass
