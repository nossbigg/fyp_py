class MLClassifierObj:
    classifier_name = ""
    classifier = None

    score_accuracy = 0
    score_precision = 0
    score_recall = 0
    score_f1 = 0

    def __init__(self, classifier_name, classifier):
        self.classifier_name = classifier_name
        self.classifier = classifier()

        self.score_accuracy = 0
        self.score_precision = 0
        self.score_recall = 0
        self.score_f1 = 0
