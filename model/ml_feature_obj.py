class MLFeatureObj:
    feature_name = ""
    feature_data = None

    # accepts a list of MLIterationObj
    test_iterations = {}

    # accepts a list of MLClassifierStats
    classifier_stats = {}
    best_classifiers = []

    def __init__(self, feature_name, feature_data):
        self.feature_name = feature_name
        self.feature_data = feature_data
        self.test_iterations = {}

        self.best_classifiers = []
        self.classifier_stats = {}

    def get_number_of_iterations(self):
        return len(self.test_iterations)

    def deallocate_data(self):
        self.feature_data = None
        for v in self.test_iterations.values():
            v.deallocate_data()

