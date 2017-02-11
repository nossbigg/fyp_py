from sklearn.metrics import accuracy_score


class MLUtils:
  def __init__(self):
    pass

  @staticmethod
  def testML(clf, train_feature, train_label, test_feature, test_label):
    clf.fit(train_feature, train_label)
    pred = clf.predict(test_feature)
    acc = accuracy_score(test_label, pred)
    return str(acc)
