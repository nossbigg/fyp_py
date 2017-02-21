import nltk
from TweetType import TweetType
from afinn import Afinn
from nltk.corpus import sentiwordnet as swn

afinn_default = Afinn()
tokenizer_default = nltk.TweetTokenizer(preserve_case=False,
                                        reduce_len=False, strip_handles=False)


def get_tweet_type(tweet):
    if 'retweeted_status' in tweet:
        return TweetType.RETWEET
    elif tweet['is_quote_status'] is True:
        if 'quoted_status_id' in tweet:
            return TweetType.QUOTE_RETWEET
        else:
            return TweetType.INVALID
    else:
        return TweetType.NORMAL


def get_scores_swn(text, tokenizer=tokenizer_default):
    tokens = tokenizer.tokenize(text)

    pos_scores = 0.0
    neg_scores = 0.0
    obj_scores = 0.0

    for token in tokens:
        matched_words = list(swn.senti_synsets(token))
        if len(matched_words) == 0:
            continue

        sentiment = matched_words[0]
        pos_scores += sentiment.pos_score()
        neg_scores += sentiment.neg_score()
        obj_scores += sentiment.obj_score()

    pos_scores /= len(tokens)
    neg_scores /= len(tokens)
    obj_scores /= len(tokens)

    return pos_scores, neg_scores, obj_scores


def get_score_afinn(text):
    return afinn_default.score(text)
