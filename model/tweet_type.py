from enum import IntEnum


class TweetType(IntEnum):
  NORMAL = 0
  RETWEET = 1
  QUOTE_RETWEET = 2
  INVALID = 3