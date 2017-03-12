import datetime


class MLCollectionObj:
    timestamp = ""
    collection_name = ""

    # accepts a dataframe
    dataset = None

    # accepts a list of MLFeatureObj
    features_tested = {}

    # stores feature with best score
    best_feature = []

    def __init__(self, collection_name, dataset):
        self.collection_name = collection_name
        self.dataset = dataset
        self.features_tested = {}
        self.timestamp = datetime.datetime.now().isoformat()

    def get_features_tested_names(self):
        return [f.feature_name for f in self.features_tested.values()]

    def deallocate_data(self):
        self.dataset = None
        for v in self.features_tested.values():
            v.deallocate_data()
