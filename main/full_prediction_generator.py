import pandas as pd
from controller.config import Config
from controller.data_label_utils import get_all_sentiment_labels
from controller.database_service import DatabaseService
from controller.ml_utils import MLUtils
from sklearn import preprocessing

config = Config()
dbs = DatabaseService(config)

# get databases
collection_names = ['sickhillary']
# collection_names = ['sickhillary', 'mosul_battle', 'trump_cabinet', 'us_economic_policy', 'death_hoax']

# declare test parameters
n_iterations_per_classifier = 1
test_ratio = 0.2
target_label = "tweet_sentiment_label"
classifier_dict = MLUtils.get_classifiers_standard_suite()

ml_collections_result = {}

# iterate through collections
for collection_name in collection_names:
    print("Collection: " + collection_name)
    # get labelled tweets (unique)
    mongo_search_query = {"tweet_sentiment_label": {"$ne": ""}}
    mongo_filter_query = {"text": 1, "tweet_type": 1, "tweet_sentiment_label": 1}
    mongo_filter_query.update({label: 1 for label in get_all_sentiment_labels()})
    tweets = dbs.get_unique_tweets_for_collection(collection_name, filter_query=mongo_filter_query,
                                                  search_query=mongo_search_query)
    df = pd.DataFrame(tweets)

    print("Generating features...")
    # normalize features
    min_max_scaler = preprocessing.MinMaxScaler()
    for label in get_all_sentiment_labels():
        df[label] = min_max_scaler.fit_transform(df[label])

    # generate features
    df['feature_nlp_afinn_swn'] = MLUtils.gen_feature_afinn_swn(df)
    df['feature_nlp_pos'] = MLUtils.gen_feature_pos(df)
    df['feature_term_tfidf'] = MLUtils.gen_feature_term_tfidf(df)
    features_tested = ['feature_term_tfidf', 'feature_nlp_afinn_swn', 'feature_nlp_pos']
    # FIXME break up train_transform and transform for tfidf

    print("Building train suite...")
    # build train suite
    ml_col_obj = MLUtils.gen_train_suite(collection_name=collection_name, df=df, target_label=target_label,
                                         source_label_list=features_tested, n_iterations=n_iterations_per_classifier,
                                         classifier_dict=classifier_dict, test_ratio=test_ratio)

    print("Running train suite...")
    # run train suite
    MLUtils.run_train_suite(ml_col_obj)

    # find best classifiers
    MLUtils.choose_best_classifiers(ml_col_obj, classifier_dict.keys())

    # clear data
    ml_col_obj.deallocate_data()

    # add to result
    ml_collections_result[collection_name] = ml_col_obj

pass
