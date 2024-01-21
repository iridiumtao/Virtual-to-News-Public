import os

from opencc import OpenCC
from spacy.lang.zh.stop_words import STOP_WORDS


class GetStopWords():
    def __init__(self, path):
        self.path = path

    def get_word(self):
        spacy_stopwords_sim = list(STOP_WORDS)
        cc = OpenCC('s2tw')
        spacy_stopwords_tra = [cc.convert(w)+'\n' for w in spacy_stopwords_sim]
        with open(self.path, 'w+', encoding="utf-8") as f:
            f.writelines(spacy_stopwords_tra)
        return spacy_stopwords_tra
