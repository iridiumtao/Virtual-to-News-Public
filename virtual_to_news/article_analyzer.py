# %%
import jieba.analyse
import pandas as pd
import logging
from ckipnlp.pipeline import CkipPipeline, CkipDocument
from ckipnlp.container.text import TextParagraph
import re


# %%
def text_rank(sentence) -> pd.DataFrame:
    """利用 jieba 專案提供的 TextRank 演算法進行關鍵字提取

    :param 文章或句子，例如：str
    :return pd.DataFrame 含有「關鍵字」及「權重」
    """
    tr_data = jieba.analyse.textrank(sentence, withWeight=True)
    df = pd.DataFrame(tr_data, columns=["text", "weight"])
    # describe_data_frame(df)
    return df


def tf_idf(sentence) -> pd.DataFrame:
    """利用 jieba 專案提供的 TF-IDF 演算法進行關鍵字提取

    :param 文章或句子，例如：str
    :return pd.DataFrame 含有「關鍵字」及「權重」
    """
    tf_idf_data = jieba.analyse.extract_tags(sentence, withWeight=True)
    df = pd.DataFrame(tf_idf_data, columns=["text", "weight"])
    # describe_data_frame(df)
    return df


def describe_data_frame(df: pd.DataFrame):
    """以 logging.debug 的方式描述 DataFrame 中的資料
    需要在 main.py 設定 logging.basicConfig(level=logging.DEBUG)
    """
    logging.debug("回傳列數與欄數:")
    logging.debug(df.shape)  # 回傳列數與欄數
    logging.debug("---")
    logging.debug("回傳描述性統計:")
    logging.debug(df.describe())  # 回傳描述性統計
    logging.debug("---")
    logging.debug("回傳前三筆觀測值 ")
    logging.debug(df.head(3))  # 回傳前三筆觀測值
    logging.debug("---")
    logging.debug("回傳後三筆觀測值")
    logging.debug(df.tail(3))  # 回傳後三筆觀測值
    logging.debug("---")
    logging.debug("回傳欄位名稱")
    logging.debug(df.columns)  # 回傳欄位名稱
    logging.debug("---")
    logging.debug("回傳 index")
    logging.debug(df.index)  # 回傳 index
    logging.debug("---")
    logging.debug("回傳資料內容")
    logging.debug(df.info)  # 回傳資料內容


def get_article_keywords(article: str) -> pd.Series:
    """取得文章標籤

    以 Series 回傳文章標籤
    透過 TextRank 進行文章分析，將 weight > 0.6 的標籤回傳
    """
    df_text_rank = text_rank(article)
    top_keywords = df_text_rank.loc[df_text_rank["weight"] > 0.6]
    tr_keywords = pd.Series(top_keywords["text"])

    # 由於 tf-idf 成效不彰，僅使用TextRank演算法作為關鍵字依據
    # df_tf_idf = tf_idf(article)
    # tf_idf_keywords = pd.Series(df_tf_idf["text"])[:5]

    df_ner = get_article_ner(article=article)
    ner_keywords = pd.Series(df_ner["word"])

    # 串接兩個 Series
    keywords = pd.concat([tr_keywords, ner_keywords])
    keywords.reset_index(drop=True, inplace=True)

    return keywords


def get_article_ner(article: str = None, is_database: bool = False):
    """利用 CkipNLP ToolKit 進行 NER 命名實體識別"""
    pipeline = CkipPipeline()

    if is_database:
        # !! is_database 這段可能不會真的運作 !!
        # todo: do some stuff to load database
        # sample, from experiment ipynb
        database = pd.read_json("../../assets/json/chinatimes20.json")
        database = database.transpose()
        database_series = pd.Series(database["content"])
        paragraph = TextParagraph().from_list(database_series.tolist())
        doc = CkipDocument(text=paragraph)
        pass
    elif article is not None:
        logging.info("article_analyzer(): get_article_ner(): From article")
        logging.info("article_analyzer(): get_article_ner(): Article:")
        logging.info("article_analyzer(): get_article_ner(): " + str(article))
        doc = CkipDocument(raw=article)
    else:
        # Source must be specified
        return False

    pipeline.get_ner(doc)
    logging.info("article_analyzer(): get_article_ner(): NER[:5]")
    logging.info("article_analyzer(): get_article_ner(): " + str(doc.ner[0][:5]))

    ner = pd.DataFrame(doc.ner[0])
    # Filter dataframe from NER types that we want only.
    ner_filtered = ner.loc[
        ner['ner'].str.contains('ORG|EVENT|FAC|NORP|PERSON|PRODUCT|WORK_OF_ART|GPE|LOC', flags=re.I, regex=True)]

    # Keep only duplicated words
    ner_filtered = ner_filtered[ner_filtered.duplicated('word')]

    ner_filtered.drop_duplicates("word", keep="first", inplace=True)
    ner_filtered.reset_index(drop=True, inplace=True)

    logging.info("article_analyzer(): get_article_ner(): Processed NER")
    logging.info("article_analyzer(): get_article_ner(): " + str(ner_filtered))

    return ner_filtered
