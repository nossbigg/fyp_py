from theano.gradient import np


class MLClassifierStats:
    def __init__(self, classifier_label):
        self.classifier_label = classifier_label

        self.scores_accuracy = []
        self.scores_precision = []
        self.scores_recall = []
        self.scores_f1 = []

        self.min = 0
        self.max = 0
        self.mean = 0
        self.median = 0
        self.std_dev = 0
        self.percentile_25 = 0
        self.percentile_75 = 0

        self.overall_score = 0

    def add_to_scores(self, ml_classifier_obj):
        self.scores_accuracy.append(ml_classifier_obj.score_accuracy)
        self.scores_precision.append(ml_classifier_obj.score_precision)
        self.scores_recall.append(ml_classifier_obj.score_recall)
        self.scores_f1.append(ml_classifier_obj.score_f1)

    def gen_stats(self):
        # based on accuracy only
        target_list = self.scores_accuracy

        self.min = min(target_list)
        self.max = max(target_list)
        self.mean = np.mean(target_list)
        self.median = np.median(target_list)
        self.std_dev = np.std(target_list)
        self.percentile_25 = np.percentile(target_list, 25)
        self.percentile_75 = np.percentile(target_list, 75)
