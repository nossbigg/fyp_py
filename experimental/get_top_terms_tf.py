import pandas as pd
from controller.config import Config
from controller.database_service import DatabaseService
from controller.database_utils import get_tweet_collections_only
from controller.nltk_manager import NLTKManager
from controller.preprocessing_utils import PreprocessingUtils as PPU

config = Config()
dbs = DatabaseService(config)

db = dbs.get_db()
collection_names = get_tweet_collections_only(dbs.get_collection_names())
for collection_name in collection_names:
    # get tweets
    filter_query = {"_id": 1, "text": 1, "tweet_sentiment_label": 1,
                    "tweet_score_afinn": 1, "tweet_score_swn_pos": 1,
                    "tweet_score_swn_neg": 1, "tweet_score_swn_obj": 1}
    tweets = dbs.get_unique_tweets_for_collection(collection_name, False, filter_query)

    pdAll = pd.DataFrame(tweets)

    # text preprocessing
    nltk_mgr = NLTKManager()
    text_tokens = [nltk_mgr.tokenize(text) for text in pdAll['text']]
    text_tokens = [PPU.removeTokenByLength(tokens, 3, 20) for tokens in text_tokens]
    text_tokens = [PPU.removeTokenHTTP(tokens) for tokens in text_tokens]
    text_tokens = [PPU.removeTokenUserReference(tokens) for tokens in text_tokens]
    text_tokens = [PPU.removeTokenHashtag(tokens) for tokens in text_tokens]
    text_tokens = [nltk_mgr.remove_stopword_tokens(tokens) for tokens in text_tokens]
    text_tokens = [nltk_mgr.lemmatize_tokens(tokens) for tokens in text_tokens]

    # gen global term frequencies
    totalFreq = nltk_mgr.gen_freq_dist([item for sublist in text_tokens for item in sublist])
    termsSelected = PPU.getTermsWithinStdDev(totalFreq, -2, 3)

    print("Top terms for '" + collection_name + "' : " + " ,".join(termsSelected))

    # TODO look at tfidfvectorizer, preprocessor
    pass
