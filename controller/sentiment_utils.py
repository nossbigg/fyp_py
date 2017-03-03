import os

from controller.data_label_utils import POS_TAG_UNIVERSAL_DICT
from nltk.corpus import sentiwordnet as swn, nps_chat
from tweet_type import TweetType

POS_TAG_UNIVERSAL_DICT_REVERSE = {v: k for k, v in POS_TAG_UNIVERSAL_DICT.iteritems()}


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


def get_scores_swn(tokens, normalize=False):
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

    if normalize:
        normalize_factor = float(len(tokens))
        pos_scores /= normalize_factor
        neg_scores /= normalize_factor
        obj_scores /= normalize_factor

    return pos_scores, neg_scores, obj_scores


def get_score_afinn(text, afinn_obj):
    return afinn_obj.score(text)


def get_nltk_nps_corpus():
    posts = []

    for xml_file in nps_chat.xml_posts():
        post_one = []
        for post in xml_file:
            t = post[0]
            at = t.attrib
            post_one.append([at['word'], at['pos']])
        posts.append(post_one)

    return posts


def get_pos_tags(tokens, pos_tagger, tag_convert_dict=None, normalize=False):
    pos_dict_count = {}

    # Get tag for given word
    for word, tag in pos_tagger.tag(tokens):
        if tag not in pos_dict_count:
            pos_dict_count[tag] = 1
        else:
            pos_dict_count[tag] += 1

    # normalize if required
    if normalize:
        normalize_factor = float(len(tokens))
        for k, v in pos_dict_count.iteritems():
            pos_dict_count[k] = v / normalize_factor

    # Perform tag conversion (if convert dict supplied)
    is_convert_tag = tag_convert_dict is not None
    if is_convert_tag:
        temp_dict = {}
        for source_tag, count in pos_dict_count.iteritems():
            if source_tag not in tag_convert_dict:
                source_tag = "X"
            target_tag = tag_convert_dict[source_tag]
            temp_dict[target_tag] = count

        pos_dict_count = temp_dict

    return pos_dict_count


def pos_tags_universal_to_mongo_dict(pos_dict):
    # ensure 0 representation for all tags
    mongo_dict = {field: 0 for field in POS_TAG_UNIVERSAL_DICT.keys()}

    for tag in POS_TAG_UNIVERSAL_DICT_REVERSE:
        if tag not in pos_dict:
            continue

        db_field_name = POS_TAG_UNIVERSAL_DICT_REVERSE[tag]
        mongo_dict[db_field_name] = pos_dict[tag]

    return mongo_dict


def get_nps_tag_convert_dict(tag_filepath):
    pos_dict = {}

    if not os.path.isfile(tag_filepath):
        return pos_dict

    with open(tag_filepath, 'rb') as f:
        for line in f:
            line = line.strip()
            pb_tag, universal_tag = line.split("\t")
            pb_tag = str.upper(pb_tag)
            universal_tag = str.upper(universal_tag)
            pos_dict[pb_tag] = universal_tag

    return pos_dict
