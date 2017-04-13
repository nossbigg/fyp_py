class MLFeatureObj:
    feature_name = ""
    feature_data = None
    gen_feature_method = None

    # accepts a list of MLIterationObj
    test_iterations = {}

    # accepts a list of MLClassifierStats
    classifier_stats = {}
    best_classifiers = []

    def __init__(self, feature_name, gen_feature_method):
        self.feature_name = feature_name
        self.gen_feature_method = gen_feature_method
        self.test_iterations = {}

        self.best_classifiers = []
        self.classifier_stats = {}

    def get_number_of_iterations(self):
        return len(self.test_iterations)

    def deallocate_data(self):
        self.feature_data = None
        for v in self.test_iterations.values():
            v.deallocate_data()

    def get_json(self):
        d = {
            "feature_name": self.feature_name,
            "best_classifiers": self.best_classifiers
        }

        test_iterations = {}
        for k, v in self.test_iterations.iteritems():
            test_iterations[k] = v.get_json()
        d["test_iterations"] = test_iterations

        classifier_stats = {}
        for k, v in self.classifier_stats.iteritems():
            classifier_stats[k] = v.get_json()
        d["classifier_stats"] = classifier_stats

        return d
