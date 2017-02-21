import math
from textblob import TextBlob as tb


# ref: http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/
class TextBlobUtils:
  @staticmethod
  def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

  @staticmethod
  def n_containing(word, bloblist):
    return 1 + sum(1 for blob in bloblist if word in blob)

  @staticmethod
  def idf(word, bloblist):
    return math.log(float(1 + len(bloblist)) /
                    float(TextBlobUtils.n_containing(word, bloblist)))

  @staticmethod
  def tfidf(word, blob, bloblist):
    return TextBlobUtils.tf(word, blob) * TextBlobUtils.idf(word, bloblist)

  @staticmethod
  def makeTb(text):
    return tb(text)
