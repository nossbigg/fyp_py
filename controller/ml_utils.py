import random

import math

import operator
import pandas as pd
from controller import preprocessing_utils as PPU
from controller.TextBlobUtils import TextBlobUtils as TBU
from controller.data_label_utils import SCORE_AFINN_LABEL, SCORE_SWN_LABELS, POS_TAG_UNIVERSAL_DICT
from controller.nltk_manager import NLTKManager as NLTKMgr
from ml_classifier_obj import MLClassifierObj
from ml_classifier_stats import MLClassifierStats
from ml_collection_obj import MLCollectionObj
from ml_feature_obj import MLFeatureObj
from ml_iteration_obj import MLIterationObj
from sklearn import svm, tree, linear_model, naive_bayes, ensemble, neural_network
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class MLUtils:
    def __init__(self):
        pass

    # Classifier Generator Functions
    @staticmethod
    def clfSVC(randnum=0):
        if randnum == 0: randnum = MLUtils.genRandomNumber()
        return svm.SVC(random_state=randnum)

    @staticmethod
    def clfDT(randnum=0):
        if randnum == 0: randnum = MLUtils.genRandomNumber()
        return tree.DecisionTreeClassifier(random_state=randnum)

    @staticmethod
    def clfLR(randnum=0):
        if randnum == 0: randnum = MLUtils.genRandomNumber()
        return linear_model.LogisticRegression(random_state=randnum)

    @staticmethod
    def clfNBBernoulli():
        return naive_bayes.BernoulliNB()

    @staticmethod
    def clfNBMultinomial():
        return naive_bayes.MultinomialNB()

    @staticmethod
    def clfRFR():
        return ensemble.RandomForestClassifier()

    @staticmethod
    def clfGRB():
        return ensemble.GradientBoostingClassifier()

    @staticmethod
    def clfNN(randnum=0):
        if randnum == 0: randnum = MLUtils.genRandomNumber()
        return neural_network.MLPClassifier(solver='lbfgs',
                                            alpha=1e-5, hidden_layer_sizes=(15,), random_state=randnum)

    @staticmethod
    def get_classifiers_standard_suite():
        return {
            "SVM": MLUtils.clfSVC,
            "DT": MLUtils.clfDT,
            "LR": MLUtils.clfLR,
            "NBBernoulli": MLUtils.clfNBBernoulli,
            "NBMulti": MLUtils.clfNBMultinomial,
            "RFR": MLUtils.clfRFR,
            "GRB": MLUtils.clfGRB,
            "NN": MLUtils.clfNN
        }

    @staticmethod
    def genRandomNumber():
        return random.randint(0, 1000)

    # Feature functions
    @staticmethod
    def gen_feature_afinn_swn(df):
        return_vec = []
        for index, row in df.iterrows():
            temp_vec = [row[SCORE_AFINN_LABEL]] + row[SCORE_SWN_LABELS].tolist()
            return_vec.append(temp_vec)

        return return_vec

    @staticmethod
    def gen_feature_pos(df):
        return_vec = []
        for index, row in df.iterrows():
            temp_vec = []
            for label in POS_TAG_UNIVERSAL_DICT.keys():
                temp_vec.append(row[label])

            return_vec.append(temp_vec)

        return return_vec

    @staticmethod
    def gen_feature_term_tfidf(df):
        return_vec = []

        nltkMgr = NLTKMgr()
        text_tokens = [nltkMgr.tokenize(text) for text in df['text']]

        # text preprocessing
        text_tokens = [PPU.PreprocessingUtils.removeTokenHTTP(tokens) for tokens in text_tokens]
        text_tokens = [PPU.PreprocessingUtils.removeTokenUserReference(tokens) for tokens in text_tokens]
        text_tokens = [PPU.PreprocessingUtils.removeTokenHashtag(tokens) for tokens in text_tokens]
        text_tokens = [nltkMgr.remove_stopword_tokens(tokens) for tokens in text_tokens]
        text_tokens = [nltkMgr.lemmatize_tokens(tokens) for tokens in text_tokens]
        text_tokens = [PPU.PreprocessingUtils.removeTokenByLength(tokens, 3, 999) for tokens in text_tokens]

        # tf-idf
        tfidf_v = TfidfVectorizer(max_features=100)
        x_train = tfidf_v.fit_transform([PPU.PreprocessingUtils.tokensToWord(tokens) for tokens in text_tokens])

        # format to correct data format for pd
        x_train = x_train.toarray().tolist()

        return x_train

    # Train functions
    @staticmethod
    def testML(clf, train_feature, train_label, test_feature, test_label):
        clf.fit(train_feature, train_label)
        pred = clf.predict(test_feature)
        acc = accuracy_score(test_label, pred)
        return str(acc)

    @staticmethod
    def testMultipleMLWithIter(ml_list, n_iterations, df):
        acc_list_total = []

        ml_keys_alphabetical = sorted(ml_list.keys())

        for i in range(1, n_iterations + 1):
            acc_list = []

            train, test = train_test_split(df, test_size=0.2)
            train_feature = pd.np.array(train["ml_vec_bin"].tolist())
            train_label = pd.np.array(train["tweet_sentiment_label"].tolist())
            test_feature = pd.np.array(test["ml_vec_bin"].tolist())
            test_label = pd.np.array(test["tweet_sentiment_label"].tolist())

            for key in ml_keys_alphabetical:
                clf = ml_list[key]()
                clf.fit(train_feature, train_label)
                pred = clf.predict(test_feature)
                acc = accuracy_score(test_label, pred)
                acc_list.append(acc)
            acc_list_total.append(acc_list)
            print("Progress: " + str(float(i) / n_iterations * 100) + "%")

        return acc_list_total

    @staticmethod
    def gen_train_suite(collection_name, df, target_label, source_label_list, n_iterations, classifier_dict,
                        test_ratio=0.2):
        # Collection level
        ml_col_obj = MLCollectionObj(collection_name=collection_name, dataset=df)

        # Features
        features_tested = {f: MLFeatureObj(f, df[f]) for f in source_label_list}
        ml_col_obj.features_tested = features_tested

        for feature_label, v in features_tested.iteritems():
            test_iterations = {}
            features_tested[feature_label].test_iterations = test_iterations

            # Iterations
            for n in range(1, n_iterations + 1):
                # split data
                train, test = train_test_split(df, test_size=test_ratio)
                train_feature = pd.np.array(train[feature_label].tolist())
                train_label = pd.np.array(train[target_label].tolist())
                test_feature = pd.np.array(test[feature_label].tolist())
                test_label = pd.np.array(test[target_label].tolist())

                ml_iter_obj = MLIterationObj(train_feature, train_label, test_feature, test_label)
                test_iterations[n] = ml_iter_obj

                # Classifiers
                for clf_name, clf_lambda in classifier_dict.iteritems():
                    ml_iter_obj.classifiers_tested[clf_name] = MLClassifierObj(clf_name, clf_lambda)

        return ml_col_obj

    @staticmethod
    def run_train_suite(ml_collection_obj):
        for feature_obj in ml_collection_obj.features_tested.values():
            print("Feature: " + feature_obj.feature_name)

            for n, iteration_obj in feature_obj.test_iterations.iteritems():
                print("Iteration: " + str(n))
                # shorthand
                ito = iteration_obj
                for clf_obj in iteration_obj.classifiers_tested.values():
                    clf = clf_obj.classifier
                    clf.fit(ito.train_feature, ito.train_label)
                    pred = clf.predict(ito.test_feature)

                    clf_obj.score_accuracy = accuracy_score(ito.test_label, pred)
                    # TODO add more scores

        return ml_collection_obj

    @staticmethod
    def choose_best_classifiers(ml_collection_obj, classifier_labels):
        SCORING_WEIGHT_MIN = 0.25
        SCORING_WEIGHT_STD_DEV = 0.5
        SCORING_WEIGHT_MEDIAN = 0.25

        for feature_obj in ml_collection_obj.features_tested.values():
            # instantiate stats
            feature_obj.classifier_stats = {l: MLClassifierStats(l) for l in classifier_labels}

            # collect classifier performance
            for iteration_obj in feature_obj.test_iterations.values():
                for clf_name, clf_obj in iteration_obj.classifiers_tested.iteritems():
                    feature_obj.classifier_stats[clf_name].add_to_scores(clf_obj)

            # compute stats
            for v in feature_obj.classifier_stats.values():
                v.gen_stats()

        # score and set best classifiers
        classifiers_count = len(ml_collection_obj.features_tested)
        for feature_obj in ml_collection_obj.features_tested.values():
            # choose the model with
            # highest min (use absolute)
            sorted_min = [c for c in feature_obj.classifier_stats.values()]
            list.sort(sorted_min, key=lambda k: k.min, reverse=False)
            for index, c in enumerate(sorted_min):
                c.overall_score += SCORING_WEIGHT_MIN * c.min

            # lowest std dev (use absolute power 2)
            sorted_std_dev = [c for c in feature_obj.classifier_stats.values()]
            list.sort(sorted_std_dev, key=lambda k: math.pow(k.std_dev, 2), reverse=True)
            for index, c in enumerate(sorted_std_dev):
                c.overall_score += SCORING_WEIGHT_STD_DEV * math.pow(c.std_dev, 2)

            # highest median (use absolute)
            sorted_median = [c for c in feature_obj.classifier_stats.values()]
            list.sort(sorted_median, key=lambda k: k.median, reverse=False)
            for index, c in enumerate(sorted_median):
                c.overall_score += SCORING_WEIGHT_MEDIAN * c.median

            # set best classifier
            sorted_classifiers = [c for c in feature_obj.classifier_stats.values()]
            list.sort(sorted_classifiers, key=lambda k: k.overall_score, reverse=True)
            feature_obj.best_classifiers.append(sorted_classifiers[0].classifier_label)

        # select best feature
        feature_scores = {}
        for feature_label, feature_obj in ml_collection_obj.features_tested.iteritems():
            best_classifier_label = feature_obj.best_classifiers[0]
            best_classifier_score = feature_obj.classifier_stats[best_classifier_label].overall_score
            feature_scores[feature_label] = best_classifier_score
        sorted_feature_scores = sorted(feature_scores.items(), key=operator.itemgetter(1))
        sorted_feature_scores.reverse()
        ml_collection_obj.best_feature.append(sorted_feature_scores[0][0])
