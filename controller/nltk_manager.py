from nltk import TweetTokenizer, PorterStemmer, FreqDist
from nltk.corpus import stopwords


# TODO refactor: extract methods, remove class
class NLTKManager():
    stopWordList = stopwords.words('english')
    tokenizer = TweetTokenizer(preserve_case=False,
                               reduce_len=False, strip_handles=False)
    stemmer = PorterStemmer()

    def __init__(self):
        pass

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)

    def removeStopwordTokens(self, tokens):
        return [w for w in tokens if not w in self.stopWordList]

    def lemmatizeTokens(self, tokens):
        return [self.stemmer.stem(w) for w in tokens]

    @staticmethod
    def genFreqDist(tokens):
        return FreqDist(tokens)

    @staticmethod
    def genFreqVector(tokens, tokensToSelect, isBinary=False):
        freqDist = FreqDist(tokens)
        termsFreq = []
        for term in tokensToSelect:
            if term in freqDist:
                termsFreq.append(freqDist[term])
            else:
                termsFreq.append(0)

        if isBinary:
            termsFreq = [1 if freq > 0 else 0 for freq in termsFreq]

        termsFreq = [float(v) for v in termsFreq]

        return termsFreq
