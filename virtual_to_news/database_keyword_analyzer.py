import jieba.analyse
import pandas as pd
import logging

import virtual_to_news.article_analyzer as analyzer


def database_keyword_analyzer(source_path: str, output_path: str):
    """
    讀取 category=null 的新聞的 json 資料庫，往 output_path 寫入包含分析好的 category 的 json。

    Parameters
    ----------
    :param source_path: 路徑需要包含檔名與副檔名。category=null 的新聞的 json 資料庫路徑
    :param output_path: 路徑需要包含檔名與副檔名。分析好的 category 的 json路徑
    """

    # read json database
    database = pd.read_json(source_path)
    database = database.transpose()

    # get content of articles
    database_series = pd.Series(database["content"])

    # analyze articles and generate categories
    list_tags = []
    for article in database_series:
        list_tags.append(analyzer.get_article_keywords(article).tolist())
    database["category"] = list_tags

    # write to json
    database.to_json(output_path, orient='index', force_ascii=False, indent=4)
