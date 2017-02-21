import random

import pandas as pd
from sklearn import svm, tree, linear_model, naive_bayes, ensemble, neural_network

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class MLUtils:
  def __init__(self):
    pass

  @staticmethod
  def genRandomNumber():
    return random.randint(0, 1000)

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
  def testML(clf, train_feature, train_label, test_feature, test_label):
    clf.fit(train_feature, train_label)
    pred = clf.predict(test_feature)
    acc = accuracy_score(test_label, pred)
    return str(acc)

  @staticmethod
  def testMultipleMLWithIter(ml_list, n_iterations, df):
    acc_list_total = []

    ml_keys_alphabetical = sorted(ml_list.keys())

    for i in range(1, n_iterations+1):
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
