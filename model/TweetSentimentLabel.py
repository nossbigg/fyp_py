from enum import Enum


class TweetSentimentLabel(Enum):
  SUPPORT = 's'
  DENY = 'd'
  NEUTRAL = 'n'
  UNRELATED = 'u'
