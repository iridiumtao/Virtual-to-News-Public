import math
import os

import pandas as pd


class TFIDF():
    def __init__(self, contents_sentences: str):
        # 文章句子合併
        contents_words = []
        # 全部合併
        pure_words = []
        for content_sentences in contents_sentences:
            words = []
            for sentence_words in content_sentences:
                words.extend(sentence_words)
            contents_words.append(words)
            pure_words.extend(words)
        self.contents_words = contents_words
        self.pure_words = pure_words

    def tf(self):
        # term frequency 計算
        tf_dict = []
        for content_words in self.contents_words:
            word_dict = {}
            for word in content_words:
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
            for word in word_dict.keys():
                word_dict[word] = round(word_dict[word]/len(content_words), 6)
            tf_dict.append(word_dict)
        self.tf_dict = tf_dict
        return tf_dict

    def idf(self):
        self.tf()
        contents_single_word = []
        for word in self.tf_dict:
            contents_single_word.append(list(word.keys()))

        file = './assets/occurrences_of_word.json'
        if os.path.isfile(file):
            occurrences_of_word = pd.read_json(file)['Qunatity'].to_dict()
        else:
            occurrences_of_word = {}
        for content_single_word in contents_single_word:
            for word in content_single_word:
                if word not in occurrences_of_word:
                    occurrences_of_word[word] = 1
        date_of_use_file = './assets/used_files.csv'
        files_use = pd.read_csv(date_of_use_file)['several_articles'].sum()

        # inverse_document_frequency
        idf_dict = {}
        for word in occurrences_of_word.keys():
            occurrences = occurrences_of_word[word]
            idf_dict[word] = math.log(round(files_use/occurrences, 4))
        self.idf_dict = idf_dict
        return idf_dict

    def tf_idf(self):
        self.tf()
        self.idf()
        tf_idf_contents = []
        for i, words in enumerate(self.tf_dict):
            tf_idf_dict = {}
            for word, freq in words.items():
                tf_idf_dict[word] = freq*self.idf_dict[word]
            tf_idf_contents.append(tf_idf_dict)
        self.tf_idf_contents = tf_idf_contents
        return tf_idf_contents
