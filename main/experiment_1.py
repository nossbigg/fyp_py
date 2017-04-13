import pandas as pd
from controller.config import Config
from controller.data_label_utils import get_all_sentiment_labels
from controller.database_service import DatabaseService
from controller.ml_utils import MLUtils

config = Config()
dbs = DatabaseService(config)

# get databases
collection_names = ['sickhillary', 'baghdadi_dead', 'death_hoax',
                    'mosul_battle', 'us_economic_policy', 'trump_cabinet']

# declare test parameters
description = "Experiment 1"
n_iterations_per_classifier = 100
test_ratio = 0.2
target_label = "tweet_sentiment_label"
classifier_dict = {"LR": MLUtils.clfLR}
features_tested_dict = {'feature_nlp_afinn_swn': MLUtils.gen_feature_afinn_swn,
                        'feature_nlp_pos': MLUtils.gen_feature_pos}

ml_collections_result = {}

# iterate through collections
for collection_name in collection_names:
    print("Collection: " + collection_name)
    # get labelled tweets (unique)
    mongo_search_query = {"tweet_sentiment_label": {"$exists": True}}
    mongo_filter_query = {"text": 1, "tweet_type": 1, "tweet_sentiment_label": 1}
    mongo_filter_query.update({label: 1 for label in get_all_sentiment_labels()})
    tweets = dbs.get_unique_tweets_for_collection(collection_name, filter_query=mongo_filter_query,
                                                  search_query=mongo_search_query)
    df = pd.DataFrame(tweets)

    print("Building train suite...")
    # build train suite
    ml_col_obj = MLUtils.gen_train_suite(collection_name=collection_name, df=df, target_label=target_label,
                                         source_label_dict=features_tested_dict,
                                         n_iterations=n_iterations_per_classifier,
                                         classifier_dict=classifier_dict, test_ratio=test_ratio,
                                         description=description)

    print("Running train suite...")
    # run train suite
    MLUtils.run_train_suite(ml_col_obj)

    # find best classifiers
    MLUtils.choose_best_classifiers(ml_col_obj, classifier_dict.keys())

    # clear data
    ml_col_obj.deallocate_data()

    # add to result
    ml_collections_result[collection_name] = ml_col_obj

print("Saving test results...")
ml_collections_result_json = {k: v.get_json() for k, v in ml_collections_result.iteritems()}
MLUtils.persist_ml_test_result(config.get_ml_test_results_dir(),
                               ml_collections_result_json, file_suffix=description)
