from ast import Str
from unicodedata import category
import pandas as pd
from ckip_transformers.nlp import CkipWordSegmenter
from textrank4zh import TextRank4Keyword

import jieba.analyse
from ckipnlp.pipeline import CkipPipeline, CkipDocument
from ckipnlp.container.text import TextParagraph
import re


class ArticleAnalyzer():
    """The article driver.

    """

    def __init__(self, article_list: list):
        self.article_list = article_list

    def get_doc(title: str = None,
                content: str = None,
                source_path: str = None,
                has_title: bool = True):
        """Single articles or json articles to list
        """
        article_list = []
        if (has_title and content != None) or \
                (title != None and content != None):
            pass
        elif source_path != None:
            database = pd.read_json(source_path)
            database = database.transpose()
            title = database["title"][:]
            content = database["content"][:]
        else:
            # Source must be specified
            return False

        if has_title:
            if type(content) is str:
                article_list = [title + '。\n' + content]
            else:
                for title, content in zip(title, content):
                    article_list.append(title + '。\n' + content)
        else:
            if type(content) is str:
                article_list = [content]
            else:
                article_list = content
        return article_list

    def save_keywords(keywords: str = None,
                      keywords_jieba: str = None,
                      noun_Pipeline: str = None,
                      source_path: str = None,
                      output_path: str = None):
        database = pd.read_json(source_path).transpose()[:]
        # keyword_list = pd.DataFrame((zip(keywords, keywords_jieba, noun_Pipeline)),
        #                   columns=['keywords', 'keywords_jieba', 'noun_Pipeline'])
        if keywords != None:
            database.insert(5, column="keywords", value=keywords)
        if keywords_jieba != None:
            database.insert(5, column="keywords_jieba", value=keywords_jieba)
        if noun_Pipeline != None:
            database.insert(5, column="noun_Pipeline", value=noun_Pipeline)
        database.to_json(output_path, orient='index',
                         force_ascii=False, indent=4)

    def word_segmenter_to_space(self):
        """Word segmenter to space
        """
        ws_driver = CkipWordSegmenter(level=3, device=0)
        # batch_size=256, max_length=128
        ws = ws_driver(self.article_list, use_delim=True)
        word_space_list = []
        for tokens in ws:
            token_str = " ".join(tokens)
            word_space_list.append(token_str)
        return word_space_list

    def get_keywords(self):
        """Use CkipWordSegmenter and TextRank4Keyword to get keyword
        """
        # text_list = self.word_segmenter_to_space()
        text_list = self.article_list
        tr4w = TextRank4Keyword()
        keywords_list = []
        # for text in text_list:
        #     tr4w.analyze(text=text, lower=True, window=2)
        #     top_keywords = tr4w.get_keywords(5, word_min_len=1)
        #     df_keywords = pd.DataFrame(
        #         top_keywords, columns=['word', 'weight'])
        #     df_keywords = df_keywords["word"].tolist()
        #     keywords_list.append(df_keywords)
        # return keywords_list

        tr4w.analyze(text=text_list, lower=True, window=2)
        top_keywords = tr4w.get_keywords(5, word_min_len=1)
        # df_keywords = pd.DataFrame(
        #     top_keywords, columns=['word', 'weight'])
        # df_keywords = df_keywords["word"].tolist()
        # keywords_list.append(df_keywords)
        return top_keywords

    def get_noun_Pipeline(self):
        """Use CkipPipeline to get noun
        """
        pipeline = CkipPipeline()
        text_sentence = TextParagraph().from_list(self.article_list)
        doc = CkipDocument(text=text_sentence)
        pipeline.get_ner(doc)
        keywords_list = []
        for ner in doc.ner:
            df_ner = pd.DataFrame(ner)

            # Filter dataframe from NER types that we want only.
            ner_filtered = df_ner.loc[
                df_ner['ner'].str.contains('ORG|EVENT|FAC|NORP|PERSON|PRODUCT|WORK_OF_ART|GPE|LOC', flags=re.I, regex=True)]

            # Keep only duplicated words
            ner_filtered = ner_filtered[ner_filtered.duplicated('word')]

            ner_filtered.drop_duplicates("word", keep="first", inplace=True)
            ner_filtered.reset_index(drop=True, inplace=True)
            top_keywords = ner_filtered["word"][:5].tolist()
            keywords_list.append(top_keywords)
        return keywords_list

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
        return keywords_list
