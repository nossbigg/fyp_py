import pandas as pd


# TODO refactor: extract methods, remove class
class PreprocessingUtils:
    def __init__(self):
        pass
        # TODO

    @staticmethod
    def removeTokenByLength(tokens, minLength, maxLength):
        return [w for w in tokens if minLength < len(w) < maxLength]

    @staticmethod
    def removeTokenHTTP(tokens):
        return [w for w in tokens if w[:4] != "http"]

    @staticmethod
    def removeTokenUserReference(tokens):
        return [w for w in tokens if w[:1] != "@"]

    @staticmethod
    def trimTokenUserReference(tokens):
        tokensTemp = []

        for w in tokens:
            if w[:1] == "@":
                w = w[1:]

            tokensTemp.append(w)

        return tokensTemp

    @staticmethod
    def removeTokenHashtag(tokens):
        return [w for w in tokens if w[:1] != "#"]

    @staticmethod
    def trimTokenHashtag(tokens):
        tokensTemp = []

        for w in tokens:
            if w[:1] == "#":
                w = w[1:]

            tokensTemp.append(w)

        return tokensTemp

    @staticmethod
    def removeTokenByBlacklist(tokens, tokensBlacklist):
        return [w for w in tokens if w not in tokensBlacklist]

    @staticmethod
    def getTermsWithinStdDev(freqDist, lowerStdDev, upperStdDev):
        freqs = freqDist.values()

        mean = pd.np.mean(freqs)
        stdDev = pd.np.std(freqs)
        lowerLimit = mean - (stdDev * lowerStdDev)
        upperLimit = mean + (stdDev * upperStdDev)

        return [term for term in freqDist if lowerLimit < freqDist[term] < upperLimit]

    @staticmethod
    def tokensToWord(tokens):
        return " ".join(tokens)
