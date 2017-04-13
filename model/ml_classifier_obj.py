from sklearn import linear_model


class MLClassifierObj:
    classifier_name = ""
    classifier = None
    clf_coefficients_values = ""
    clf_coefficients_targets = ""

    score_accuracy = 0
    score_precision = 0
    score_recall = 0
    score_f1 = 0

    def __init__(self, classifier_name, classifier):
        self.classifier_name = classifier_name
        self.classifier = classifier()
        self.clf_coefficients_values = ""
        self.clf_coefficients_targets = ""

        self.score_accuracy = 0
        self.score_precision = 0
        self.score_recall = 0
        self.score_f1 = 0

    def get_json(self):
        d = {
            "classifier_name": self.classifier_name,
            "clf_coefficients_values": str(self.clf_coefficients_values),
            "clf_coefficients_targets": str(self.clf_coefficients_targets),

            "score_accuracy": self.score_accuracy,
            "score_precision": self.score_precision,
            "score_recall": self.score_recall,
            "score_f1": self.score_f1
        }

        return d

    def persist_coefficients(self):
        if isinstance(self.classifier, linear_model.LogisticRegression):
            self.clf_coefficients_targets = self.classifier.classes_
            self.clf_coefficients_values = self.classifier.coef_
