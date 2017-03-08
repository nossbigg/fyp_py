TWEET_TYPE_LABEL = "tweet_type"
SCORE_AFINN_LABEL = "tweet_score_afinn"
SCORE_SWN_LABELS = ["tweet_score_swn_pos", "tweet_score_swn_neg", "tweet_score_swn_obj"]
POS_TAG_UNIVERSAL_DICT = {
    "tweet_score_pos_u_adj": "ADJ",
    "tweet_score_pos_u_adp": "ADP",
    "tweet_score_pos_u_adv": "ADV",
    "tweet_score_pos_u_conj": "CONJ",
    "tweet_score_pos_u_det": "DET",
    "tweet_score_pos_u_noun": "NOUN",
    "tweet_score_pos_u_num": "NUM",
    "tweet_score_pos_u_prt": "PRT",
    "tweet_score_pos_u_pron": "PRON",
    "tweet_score_pos_u_verb": "VERB",
    "tweet_score_pos_u_dot": ".",
    "tweet_score_pos_u_x": "X",
}


def get_score_afinn_label():
    return SCORE_AFINN_LABEL


def get_swn_score_labels():
    return SCORE_SWN_LABELS


def get_pos_tags_labels():
    return POS_TAG_UNIVERSAL_DICT.keys()


def get_all_sentiment_labels():
    return [get_score_afinn_label()] + get_swn_score_labels() + get_pos_tags_labels()
