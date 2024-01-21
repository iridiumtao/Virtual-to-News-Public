import os

import pandas as pd
from loguru import logger


class FileManagement():
    """The article driver.
    """
    def __init__(self, source_path: str = None):
        """Single articles or json articles to list
        """
        self.source_path = source_path
        self.contents = None

        self.keywords = None
        self.keywords_t = None
        self.nouns_ner = None
        self.keywords_jieba = None
        self.nouns_pipeline = None

        self.contents_word_segmenter = None
        self.contents_pos_tagger = None
        self.contents_no_filter = None
        self.contents_no_stop_words = None
        self.contents_all_filters = None
        self.contents_numerical_value = None
        self.textrank_weights = None
        self.weights = None

    def to_articles(self,
                    title: str = None,
                    content: str = None,
                    has_title: bool = False):
        source_path = self.source_path
        articles = []
        if (not has_title and content is not None) or \
                (title is not None and content is not None):
            if has_title:
                articles = [title + '。\n' + content]
            else:
                articles = [content]
        elif source_path is not None:
            database = pd.read_json(source_path).transpose()

            if has_title:
                articles = (database["title"] + '。\n' +
                            database["content"]).tolist()
            else:
                articles = database["content"].tolist()
        else:
            articles = []

        self.contents = articles

    def get_data(self):
        database = pd.read_json(self.source_path).transpose()
        columns = database.columns
        if 'content_keywords_tt' in columns:
            self.content_keywords_tt = database['content_keywords_tt'].to_list(
            )
        if 'textrank_weights' in columns:
            self.textrank_weights = database['textrank_weights'].to_list()

        if 'contents_word_segmenter' in columns:
            self.contents_word_segmenter = database[
                'contents_word_segmenter'].to_list()
        if 'contents_pos_tagger' in columns:
            self.contents_pos_tagger = database['contents_pos_tagger'].to_list(
            )

        if 'contents_no_filter' in columns:
            self.contents_no_filter = database['contents_no_filter'].to_list()
        if 'contents_no_stop_words' in columns:
            self.contents_no_stop_words = database[
                'contents_no_stop_words'].to_list()
        if 'contents_all_filters' in columns:
            self.contents_all_filters = database[
                'contents_all_filters'].to_list()
        if 'contents_numerical_value' in columns:
            self.contents_numerical_value = database[
                'contents_numerical_value'].to_list()

        if 'nouns_ner' in columns:
            self.nouns_ner = database['nouns_ner'].to_list()

    def segmentation(self):
        database_json = pd.read_json(self.source_path)
        index = database_json.index
        database = database_json.transpose()
        contents_no_filter = None
        contents_no_stop_words = None
        contents_all_filters = None
        contents_numerical_value = None
        if 'contents_no_filter' in index:
            contents_no_filter = database["contents_no_filter"].to_list()
        if 'contents_no_stop_words' in index:
            contents_no_stop_words = database[
                "contents_no_stop_words"].to_list()
        if 'contents_all_filters' in index:
            contents_all_filters = database["contents_all_filters"].to_list()
        if 'contents_numerical_value' in index:
            contents_numerical_value = database[
                "contents_numerical_value"].to_list()
        return contents_no_filter, contents_no_stop_words, contents_all_filters, contents_numerical_value

    def segmenter_and_tagger(self):
        database_json = pd.read_json(self.source_path)
        index = database_json.index
        database = database_json.transpose()
        contents_word_segmenter = None
        contents_pos_tagger = None
        if 'contents_word_segmenter' in index:
            contents_word_segmenter = database[
                "contents_word_segmenter"].to_list()
        if 'contents_pos_tagger' in index:
            contents_pos_tagger = database["contents_pos_tagger"].to_list()
        return contents_word_segmenter, contents_pos_tagger

    def save_converted(converted,
                       source_path: str = None,
                       destination_path: str = None):
        database = pd.read_json(source_path).transpose()[:]
        con_col = converted.columns
        for data_col in database.columns:
            if data_col in con_col:
                database = database.drop(data_col, axis=1)
        database = pd.concat([database, converted], axis=1)

        if not os.path.isdir(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path))
        database.to_json(destination_path,
                         orient='index',
                         force_ascii=False,
                         indent=4)

    def save_all_exists(self,
                        source_path: str = None,
                        destination_path: str = None):
        database = pd.read_json(source_path).transpose()[:]

        keywords = self.keywords
        if keywords is not None:
            database['keywords'] = keywords
        keywords_t = self.keywords_t
        if keywords_t is not None:
            database['keywords_t'] = keywords_t
        nouns_ner = self.nouns_ner
        if nouns_ner is not None:
            database['nouns_ner'] = nouns_ner
        keywords_jieba = self.keywords_jieba
        if keywords_jieba is not None:
            database['keywords_jieba'] = keywords_jieba
        nouns_pipeline = self.nouns_pipeline
        if nouns_pipeline is not None:
            database['nouns_pipeline'] = nouns_pipeline
        contents_word_segmenter = self.contents_word_segmenter
        if contents_word_segmenter is not None:
            database['contents_word_segmenter'] = contents_word_segmenter
        contents_pos_tagger = self.contents_pos_tagger
        if contents_pos_tagger is not None:
            database['contents_pos_tagger'] = contents_pos_tagger
        contents_no_filter = self.contents_no_filter
        if contents_no_filter is not None:
            database['contents_no_filter'] = contents_no_filter
        contents_no_stop_words = self.contents_no_stop_words
        if contents_no_stop_words is not None:
            database['contents_no_stop_words'] = contents_no_stop_words
        contents_all_filters = self.contents_all_filters
        if contents_all_filters is not None:
            database['contents_all_filters'] = contents_all_filters
        contents_numerical_value = self.contents_numerical_value
        if contents_numerical_value is not None:
            database['contents_numerical_value'] = contents_numerical_value
        textrank_weights = self.textrank_weights
        if textrank_weights is not None:
            database['textrank_weights'] = textrank_weights
        weights = self.weights
        if weights is not None:
            database['weights'] = weights

        if not os.path.isdir(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path))
        database.to_json(destination_path,
                         orient='index',
                         force_ascii=False,
                         indent=4)

    def according_to_target(file_list: list, topic: str,
                            classification_mode: str, source_exclude: list):
        """
        classification_mode選取文章方法：
            not_specify: 將所有新聞稿納入計算
            appears: 將所有提及主題的新聞稿納入計算
            輸入自選的 keyword_method: 尋找新聞稿中的keyword_method的list，如果其中包含主題，就將該篇新聞稿納入計算
        """
        article_list = []
        for f in file_list:
            article = pd.read_json(f).transpose()
            if classification_mode is not None or classification_mode != 'not_specify':
                if classification_mode in article.columns:
                    if article['source'][0] != source_exclude:
                        for k, c in zip(article[classification_mode],
                                        article['content']):
                            if topic in k:
                                article_list.append(c)
                elif classification_mode == 'appears':
                    if article['source'][0] != source_exclude:
                        for c in article['content']:
                            if topic in c:
                                article_list.append(c)
            else:
                if article['source'][0] != source_exclude:
                    for c in article['content']:
                        article_list.append(c)
        if article_list == []:
            logger.warning(f"topic not found in classification:{classification_mode}")
            logger.warning("Enable default selection of all articles")
            for f in file_list:
                article = pd.read_json(f).transpose()
                if article['source'][0] != source_exclude:
                    for c in article['content']:
                        article_list.append(c)
        return article_list

    def get_keywords(file_list: list, classification_mode: str,
                     source_exclude: list):
        # 尋找全部關鍵字
        articles_keywords = []
        articles_keywords_extend = articles_keywords.extend
        for f in file_list:
            news = pd.read_json(f).transpose()
            if classification_mode in news.columns:
                if news['source'][0] != source_exclude:
                    keywords = []
                    keywords_extend = keywords.extend
                    for article_keywords_list in news[classification_mode]:
                        keywords_extend(article_keywords_list)
                    articles_keywords_extend(keywords)
            else:
                logger.error("classification not found in file.")
                logger.error(f"file:{f}")
                logger.error(f"classification_mode:{classification_mode}")
        return articles_keywords

    def save_extract(filename: str, destination_path: str, content: str):
        if not os.path.isdir(destination_path):
            os.makedirs(destination_path)
        filename_path = destination_path+'/'+filename
        with open(filename_path, 'w', encoding='utf-8') as f:
            f.write(content)
