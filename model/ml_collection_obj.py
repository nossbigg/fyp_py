import datetime


class MLCollectionObj:
    timestamp = ""
    collection_name = ""
    description = ""

    # accepts a dataframe
    dataset = None

    # accepts a list of MLFeatureObj
    features_tested = {}

    # stores feature with best score
    best_feature = []

    def __init__(self, collection_name, dataset, description):
        self.timestamp = datetime.datetime.now().isoformat()
        self.collection_name = collection_name
        self.description = description

        self.dataset = dataset
        self.features_tested = {}
        self.best_feature = []

    def get_features_tested_names(self):
        return [f.feature_name for f in self.features_tested.values()]

    def deallocate_data(self):
        self.dataset = None
        for v in self.features_tested.values():
            v.deallocate_data()

    def get_json(self):
        d = {
            "timestamp": self.timestamp,
            "collection_name": self.collection_name,
            "description": self.description,
            "best_feature": self.best_feature
        }

        features_tested = {}
        for k, v in self.features_tested.iteritems():
            features_tested[k] = v.get_json()
        d["features_tested"] = features_tested

        return d
