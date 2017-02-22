import csv
import itertools

import pandas as pd
import pymongo
from controller import preprocessing_utils as PPU
from controller.MLUtils import MLUtils
from controller.nltk_manager import NLTKManager as NLTKMgr
from controller.TextBlobUtils import TextBlobUtils as TBU
from sklearn import preprocessing

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

# tf-idf
pdAll['tokens_tfidf'] = [PPU.PreprocessingUtils.tokensToWord(tokens) for tokens in text_tokens]
pdAll['tokens_tb'] = [TBU.makeTb(text) for text in pdAll['tokens_tfidf']]

allText = " ".join(pdAll['tokens_tfidf'])
allTb = TBU.makeTb(allText)
allTb_words = {word: 0 for word in allTb.words}

for blob in pdAll['tokens_tb']:
    scores = {word: TBU.tfidf(word, blob, pdAll['tokens_tb']) for word in blob.words}
    for key, value in scores.items():
        allTb_words[key] += value

# choose top terms
freqs = allTb_words.values()
mean = pd.np.mean(freqs)
stdDev = pd.np.std(freqs)
lowerLimit = mean - (stdDev * 3)
upperLimit = mean + (stdDev * 3)

termsSelected = [key for key, value in allTb_words.items()
                 if lowerLimit < value < upperLimit]

# gen global term frequencies
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

with open('ml_test_tfidf.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    ml_keys_alphabetical = sorted(ml_list.keys())

    writer.writerow(ml_keys_alphabetical)
    for acc_sublist in acc_list:
        writer.writerow(acc_sublist)
