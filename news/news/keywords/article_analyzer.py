import codecs
import os
import re

import jieba.analyse
import pandas as pd
import torch
from ckip_transformers.nlp import (CkipNerChunker, CkipPosTagger,
                                   CkipWordSegmenter)

from news.keywords import util  # from . import util
from news.keywords.get_stop_words import GetStopWords
# from .TextRank4Keyword import TextRank4Keyword
from news.keywords.tf_idf import TFIDF

# from ckipnlp.pipeline import CkipPipeline, CkipDocument
# from ckipnlp.container.text import TextParagraph


class ArticleAnalyzer():
    """The article driver.
    """

    def __init__(self,
                 content_list: list = None,
                 contents_no_filter: list = None,
                 contents_no_stop_words: list = None,
                 contents_all_filters: list = None,
                 contents_numerical_value: list = None,
                 nouns_ner: list = None,
                 contents_word_segmenter: list = None,
                 contents_pos_tagger: list = None
                 ):
        self.contents_no_filter = contents_no_filter
        self.contents_no_stop_words = contents_no_stop_words
        self.contents_all_filters = contents_all_filters
        self.contents_numerical_value = contents_numerical_value

        self.nouns_ner = nouns_ner
        self.contents_word_segmenter = contents_word_segmenter
        self.contents_pos_tagger = contents_pos_tagger

        self.article_list = content_list

    def need_processed(source_path, deal_with):
        """Determining the extraction method that the file has not used

        """
        index = pd.read_json(source_path).index
        deal_with = [name for name in deal_with if name not in index]
        return deal_with

    def merge_lr(ws_filter, combined_text, ner_left, ner_right, content_left, content_right):
        if ner_right > 0:
            if content_right+1 < len(ws_filter):
                new = ws_filter[content_right+1]
                content_right += 1
            else:
                new = " "
            combined_text = combined_text+new
            ner_right = ner_right-len(new)
        if ner_left > 0:
            if content_left-1 > 0:
                new = ws_filter[content_left-1]
                content_left -= 1
            else:
                new = " "
            combined_text = new+combined_text
            ner_left = ner_left-len(new)
        if ner_right == 0 and ner_left == 0:
            return combined_text, content_left, content_right
        elif ner_right < 0 or ner_left < 0:
            a = -ner_left
            b = len(combined_text)+ner_right
            return combined_text[a:b], content_left, content_right
        else:
            return ArticleAnalyzer.merge_lr(ws_filter, combined_text, ner_left, ner_right, content_left, content_right)

    def ws_combination_ner(nouns_ner, contents_word_segmenter):
        new_contents_word_segmenter = []
        new_contents_word_segmenter_append = new_contents_word_segmenter.append

        if nouns_ner is not None:
            for content_ners, content_ws in zip(nouns_ner, contents_word_segmenter):
                ners_filter = [ners for ners in content_ners if len(ners) > 1 and not re.match(
                    r'[a-z]+', ners, re.I)]
                ners_one_word = [
                    word for ners in ners_filter for word in ners if word != " "]
                if ners_one_word:
                    ws_filter = [ws.strip()
                                 for ws in content_ws if len(ws.strip()) == 1]
                    ws_no_blank = [ws.strip() for ws in content_ws]
                    multiple_anastomosis = [
                        t for t in ws_filter if t in ners_one_word]
                    if multiple_anastomosis:
                        multiple_anastomosis = list(set(multiple_anastomosis))
                        num = -1
                        for anastomosis in multiple_anastomosis:
                            for ner in ners_filter:
                                if anastomosis in ner:
                                    combined_text = anastomosis
                                    ner_left = ner.index(anastomosis)-0
                                    ner_right = len(
                                        ner)-ner.index(anastomosis)-1
                                    content_left = ws_no_blank.index(
                                        anastomosis)
                                    content_right = ws_no_blank.index(
                                        anastomosis)
                                    combined_text, content_left, content_right = ArticleAnalyzer.merge_lr(
                                        ws_no_blank, combined_text, ner_left, ner_right, content_left, content_right)
                                    # print(ner)
                                    # print(anastomosis)
                                    # print(combined_text,len(combined_text),len(ner))
                                    # print(content_left, content_right)
                                    if combined_text == ner:
                                        # print(f"{ner}有符合")
                                        if not num == content_left:
                                            # print("刪除")
                                            del content_ws[content_left: content_right+1]
                                            content_ws.insert(
                                                content_left, combined_text)
                                            num = content_left
                            # print('---------')
                new_contents_word_segmenter_append(content_ws)
        else:
            # print("nouns_ner is None")
            new_contents_word_segmenter = contents_word_segmenter
        return new_contents_word_segmenter

    def word_segmenter(self, ws_model_name='./assets/model/ckiplab/bert-base-chinese-ws'):
        if not os.path.isdir(ws_model_name):
            ws_model_name = 'ckiplab/bert-base-chinese-ws'
        text = self.article_list
        ws_driver = CkipWordSegmenter(device=0, model_name=ws_model_name)
        contents_word_segmenter = ws_driver(
            text, use_delim=True, delim_set='\n', show_progress=False)
        torch.cuda.empty_cache()
        return contents_word_segmenter

    def pos_tagger(self, pos_model_name='./assets/model/ckiplab/bert-base-chinese-pos'):
        if not os.path.isdir(pos_model_name):
            pos_model_name = 'ckiplab/bert-base-chinese-pos'
        pos_driver = CkipPosTagger(device=0, model_name=pos_model_name)
        contents_pos_tagger = pos_driver(
            self.contents_word_segmenter, use_delim=False, show_progress=False)
        torch.cuda.empty_cache()
        return contents_pos_tagger

    def filter(contents_word_segmenter=None,
               contents_pos_tagger=None,
               stop_words_file=None,
               allow_tags=util.allow_tags):

        if type(stop_words_file) is not str:
            # current_location = os.path.dirname(os.path.realpath(__file__))
            # stop_words_file = f'{current_location}\\stopwordsnew.txt'
            stop_words_file = './assets/stopwordsnew.txt'
            if not os.path.isfile(stop_words_file):
                GetStopWords(stop_words_file).get_word()

        # stop_words = set()
        stop_words = {}
        for i, word in enumerate(codecs.open(stop_words_file, 'r', 'utf-8', 'ignore')):
            w = word.strip()
            stop_words[w] = w.strip()

        allow_tags = [util.as_text(item) for item in allow_tags]

        words_no_filter = []
        words_no_stop = []
        words_allow_tag = []

        sentences_no_filter = []
        sentences_stop = []
        sentences_tag = []

        contents_no_filter = []
        contents_no_stop = []
        contents_allow_tag = []

        contents_numerical_value = []
        for words_ws, words_pos in zip(contents_word_segmenter, contents_pos_tagger):
            number_of_numbers = 0
            for word_ws, word_pos in zip(words_ws, words_pos):
                tag_not_exist = True  # 是否存在allow_tags，減少後續比對時間
                # 單詞組成句子
                words_no_filter.append(word_ws)
                if word_ws not in stop_words.keys():
                    words_no_stop.append(word_ws)
                    if word_pos in allow_tags:
                        words_allow_tag.append(word_ws)
                        tag_not_exist = False
                # 不同段的句子
                if tag_not_exist and word_pos == 'PERIODCATEGORY':
                    sentences_no_filter.append(words_no_filter)
                    words_no_filter = []

                    sentences_stop.append(words_no_stop)
                    words_no_stop = []

                    sentences_tag.append(words_allow_tag)
                    words_allow_tag = []
                # todo 需要放到util
                # 計算內容有多少數字
                elif tag_not_exist and word_pos in ['Neqa', 'Neqb', 'Nes', 'Neu']:
                    number_of_numbers += 1

            # todo 不是一個好寫法要更改
            contents_numerical_value.append(
                [len(words_pos), number_of_numbers, number_of_numbers/len(words_pos)])

            contents_no_filter.append(sentences_no_filter)
            contents_no_stop.append(sentences_stop)
            contents_allow_tag.append(sentences_tag)

            words_no_filter = []
            words_no_stop = []
            words_allow_tag = []

            sentences_no_filter = []
            sentences_stop = []
            sentences_tag = []
        return contents_no_filter, contents_no_stop, contents_allow_tag, contents_numerical_value

    def get_textrank(
            window=2,
            vertex_source='all_filters',
            edge_source='no_stop_words',
            words_no_filter=None,
            words_no_stop_words=None,
            words_all_filters=None,
            pagerank_config={'alpha': 0.85, }):
        # contents_no_filter=None,
        # contents_no_stop_words=None,
        # contents_all_filters=None):
        """Use CkipWordSegmenter and TextRank4Keyword to get keyword
        """

        # if not(contents_no_filter and contents_no_stop_words and contents_all_filters):
        #     content_word_segmenter, content_pos_tagger = self.word_segmenter_and_pos_tagger()
        #     contents_no_filter, contents_no_stop_words, contents_all_filters, number = self.filter(
        #         content_word_segmenter, content_pos_tagger)

        # tr4w = TextRank4Keyword()
        # tr4w.analyze(window=2,
        #              words_no_filter=contents_no_filter,
        #              words_no_stop_words=contents_no_stop_words,
        #              words_all_filters=contents_all_filters)
        # textrank_weights = tr4w.get_keywords(20, word_min_len=2)

        textrank_weights = []
        result = util.AttrDict(words_no_filter=words_no_filter,
                               words_no_stop_words=words_no_stop_words,
                               words_all_filters=words_all_filters)
        options = ['no_filter', 'no_stop_words', 'all_filters']

        if vertex_source in options:
            _vertex_source = result['words_'+vertex_source]
        else:
            _vertex_source = result['words_all_filters']

        if edge_source in options:
            _edge_source = result['words_'+edge_source]
        else:
            _edge_source = result['words_no_stop_words']

        for ver, edg in zip(_vertex_source, _edge_source):
            keywords = util.sort_words(
                ver, edg, window=window, pagerank_config=pagerank_config)
            textrank_weights.append(keywords)

        num = 20
        word_min_len = 1

        result = []
        for keywords in textrank_weights:
            keyword_list = {}
            count = 0
            for item in keywords:
                if count >= num:
                    break
                if len(item.word) >= word_min_len:
                    keyword_list[item["word"]] = item["weight"]
                    count += 1

            result.append(keyword_list)
        return result

    def tf_idf(contents_sentences, weights_name):
        tfidf = TFIDF(contents_sentences)
        tf_idf_weights = tfidf.tf_idf()
        idf_weights = tfidf.idf_dict
        tf_weights = tfidf.tf_dict
        if weights_name == 'idf':
            return idf_weights
        elif weights_name == 'tfidf':
            return tf_idf_weights
        elif weights_name == 'tf':
            return tf_weights

    def multiply(contents_weights_1, contents_weights_2=None, words_weights=None, power=2):
        contents_weights = []
        contents_weights_append = contents_weights.append
        # textrank tfidf or tf
        if contents_weights_2:
            for weights_1, weights_2 in zip(contents_weights_1, contents_weights_2):
                weights = {}
                for key, val in weights_1.items():
                    weights[key] = val*weights_2[key]**power
                    contents_weights_append(weights)
        # textrank idf
        elif words_weights:
            for weights_1 in contents_weights_1:
                weights = {}
                for key, val in weights_1.items():
                    weights[key] = val*words_weights[key]**power
                contents_weights_append(weights)
        else:
            contents_weights = contents_weights_1
        return contents_weights

    def get_keywords(self, ner=False):
        # 若無分詞和詞性，則依照文章去取得分詞和詞性
        contents_word_segmenter = self.contents_word_segmenter
        if contents_word_segmenter is None:
            contents_word_segmenter = self.word_segmenter()
        # 依照ner(實體識別)，組合分詞，不是必要可取消
        if ner:
            nouns_ner = self.nouns_ner
            if nouns_ner is None:
                nouns_ner = self.get_nouns_ner()
            contents_word_segmenter = ArticleAnalyzer.ws_combination_ner(
                nouns_ner, contents_word_segmenter)
            self.nouns_ner = nouns_ner
        self.contents_word_segmenter = contents_word_segmenter

        # 若無詞性，則依照文章去取得詞性
        contents_pos_tagger = self.contents_pos_tagger
        if contents_pos_tagger is None:
            contents_pos_tagger = self.pos_tagger()
            self.contents_pos_tagger = contents_pos_tagger

        # 篩選(停用詞過濾、詞性過濾) 和 分句(文章分句)，額外計算文章內：詞總數、數字詞總數
        contents_no_filter, contents_no_stop_words, contents_all_filters, contents_numerical_value = ArticleAnalyzer.filter(
            contents_word_segmenter, contents_pos_tagger)
        self.contents_no_filter = contents_no_filter
        self.contents_no_stop_words = contents_no_stop_words
        self.contents_all_filters = contents_all_filters
        self.contents_numerical_value = contents_numerical_value

        # textrank計算權重
        textrank_weights = ArticleAnalyzer.get_textrank(words_no_filter=contents_no_filter,
                                                        words_no_stop_words=contents_no_stop_words,
                                                        words_all_filters=contents_all_filters)
        self.textrank_weights = textrank_weights

        # tf_idf 計算權重，idf 詞總數量需要使用 occurrences_of_word.json(由occurrences_of_word.py 取得)
        file = './assets/occurrences_of_word.json'
        if os.path.isfile(file):
            idf_weights = ArticleAnalyzer.tf_idf(contents_all_filters, 'idf')
        else:
            idf_weights = None

        weights = ArticleAnalyzer.multiply(
            contents_weights_1=textrank_weights, words_weights=idf_weights, power=2)
        self.weights = weights

        keywords_t = ArticleAnalyzer.choose(contents_numerical_value, textrank_weights)
        self.keywords_t = keywords_t

        keywords = ArticleAnalyzer.choose(contents_numerical_value, weights)
        self.keywords = keywords
        return keywords

    def choose(number, contents_keywords_weights):
        ckw = []
        ckw_append = ckw.append
        for keywords_weights in contents_keywords_weights:
            keywords_sort = sorted(
                keywords_weights.items(), key=lambda x: x[1], reverse=True)
            # ckw_append(keywords_sort[:10])
            keywords_sort = [keywords[0] for keywords in keywords_sort][0:5]
            ckw_append(keywords_sort)

        # Do not give keywords because there are too many numbers
        for i, n in enumerate(number):
            if n[2] > 0.1 and n[0] < 200:
                # self.keywords[i]=[n,self.keywords[i]]
                ckw[i] = []
        return ckw

    def get_nouns_ner(self, only_duplicated=False):
        """from ckip_transformers.nlp import CkipNerChunker to get nouns
        """

        model_name = './assets/model/ckiplab/bert-base-chinese-ner'
        
        if not os.path.isdir(model_name):
            model_name = 'ckiplab/bert-base-chinese-ner'
        ner_driver = CkipNerChunker(device=0, model_name=model_name)
        ner = ner_driver(self.article_list, use_delim=True,
                         delim_set='\n', show_progress=False)
        torch.cuda.empty_cache()

        ner_list = []
        ner_append = ner_list.append
        for n in ner:
            df_ner = pd.DataFrame(n)
            if not df_ner.shape[0]:
                return None
            df_ner['word'] = df_ner['word'].str.strip()

            # Filter dataframe from NER types that we want only.
            ner_filtered = df_ner.loc[
                df_ner['ner'].str.contains('ORG|EVENT|FAC|NORP|PERSON|PRODUCT|WORK_OF_ART|GPE|LOC', flags=re.I, regex=True)]

            # Keep only duplicated words
            if only_duplicated:
                ner_filtered = ner_filtered[ner_filtered.duplicated('word')]
                ner_filtered.drop_duplicates(
                    "word", keep="first", inplace=True)
            else:
                ner_filtered = ner_filtered.drop_duplicates(
                    "word", keep="first", inplace=False)

            ner_filtered.reset_index(drop=True, inplace=True)
            ner = ner_filtered["word"].tolist()
            # top_keywords = ner_filtered["word"][:5].tolist()
            ner_append(ner)
        self.nouns_ner = ner_list
        return ner_list

    # def get_nouns_pipeline(self, only_duplicated=False):
    #     """from ckipnlp.pipeline import CkipPipeline to get nouns
    #     """
    #     pipeline = CkipPipeline()
    #     text_sentence = TextParagraph().from_list(self.article_list)
    #     doc = CkipDocument(text=text_sentence)
    #     pipeline.get_ner(doc)
    #     keywords_list = []
    #     for ner in doc.ner:
    #         df_ner = pd.DataFrame(ner)
    #         if not df_ner.shape[0]:
    #             return None

    #         # Filter dataframe from NER types that we want only.
    #         ner_filtered = df_ner.loc[
    #             df_ner['ner'].str.contains('ORG|EVENT|FAC|NORP|PERSON|PRODUCT|WORK_OF_ART|GPE|LOC', flags=re.I, regex=True)]

    #         # Keep only duplicated words
    #         if only_duplicated:
    #             ner_filtered = ner_filtered.drop_duplicates(
    #                 "word", keep="first", inplace=False)
    #         else:
    #             ner_filtered = ner_filtered[ner_filtered.duplicated('word')]
    #             ner_filtered.drop_duplicates(
    #                 "word", keep="first", inplace=True)

    #         ner_filtered.reset_index(drop=True, inplace=True)
    #         top_keywords = ner_filtered["word"][:5].tolist()
    #         keywords_list.append(top_keywords)
    #     self.nouns_pipeline = keywords_list
    #     return keywords_list

    def get_keywords_jieba(self):
        """取得文章標籤

        以 Series 回傳文章標籤
        透過 TextRank 進行文章分析，將 weight > 0.6 的標籤回傳
        """
        keywords_list = []
        for art in self.article_list:
            keywords = jieba.analyse.textrank(art, withWeight=True)
            df_keywords = pd.DataFrame(keywords, columns=["text", "weight"])
            # top_keywords = df_text_rank.loc[df_text_rank["weight"] > 0.6]
            top_keywords = df_keywords["text"][:5].tolist()
            keywords_list.append(top_keywords)
        self.keywords_jieba = keywords_list
        return keywords_list
