class MLIterationObj:
    train_feature = None
    train_label = None
    test_feature = None
    test_label = None

    # accepts a list of MLClassifierObj
    classifiers_tested = {}

    def __init__(self, train_feature, train_label, test_feature, test_label):
        self.train_feature = train_feature
        self.train_label = train_label
        self.test_feature = test_feature
        self.test_label = test_label

        self.classifiers_tested = {}
        self.best_classifiers = []

    def deallocate_data(self):
        self.train_feature = None
        self.train_label = None
        self.test_feature = None
        self.test_label = None

    def get_json(self):
        d = {}

        classifiers_tested = {}
        for k, v in self.classifiers_tested.iteritems():
            classifiers_tested[k] = v.get_json()
        d["classifiers_tested"] = classifiers_tested

        return d
