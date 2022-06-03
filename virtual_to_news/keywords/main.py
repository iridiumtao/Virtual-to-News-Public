# -*- coding:utf-8 -*-
import pandas as pd
from article_analyzer import ArticleAnalyzer as Ar


def main():
    source_path = "assets/json/test186.json"
    output_path = "assets/json/keyword/test3333_keyword.json"

    doc = Ar.get_doc(source_path=source_path, has_title=True)
    doc_Ar = Ar(doc)
    # for i in doc_Ar.word_segmenter_to_space():
    #     print(i)
    # print(doc_Ar.word_segmenter_to_space())

    keywords = None
    keywords_jieba = None
    noun_Pipeline = None

    # keywords = doc_Ar.get_keywords()  # to do :詞性 塞選
    # keywords_jieba = doc_Ar.get_keywords_jieba()
    noun_Pipeline = doc_Ar.get_noun_Pipeline()
    # print(noun_Pipeline)
    # print(keywords)

    Ar.save_keywords(
        keywords=keywords,
        keywords_jieba=keywords_jieba,
        noun_Pipeline=noun_Pipeline,
        source_path=source_path,
        output_path=output_path)


if __name__ == "__main__":
    main()
