from nltk import TweetTokenizer, PorterStemmer, FreqDist
from nltk.corpus import stopwords


class NLTKManager:
    __stopword_list = stopwords.words('english')
    __stemmer = PorterStemmer()
    __tokenizer = TweetTokenizer(preserve_case=False,
                                 reduce_len=False, strip_handles=False)

    def __init__(self):
        pass

    def tokenize(self, text):
        return self.__tokenizer.tokenize(text)

    def remove_stopword_tokens(self, tokens):
        return [w for w in tokens if not w in self.__stopword_list]

    def lemmatize_tokens(self, tokens):
        return [self.__stemmer.stem(w) for w in tokens]

    @staticmethod
    def gen_freq_dist(tokens):
        return FreqDist(tokens)

    @staticmethod
    def gen_freq_vector(tokens, tokens_to_select, is_binary=False):
        freq_dist = FreqDist(tokens)
        terms_freq = []
        for term in tokens_to_select:
            if term in freq_dist:
                terms_freq.append(freq_dist[term])
            else:
                terms_freq.append(0)

        if is_binary:
            terms_freq = [1 if freq > 0 else 0 for freq in terms_freq]

        terms_freq = [float(v) for v in terms_freq]

        return terms_freq
