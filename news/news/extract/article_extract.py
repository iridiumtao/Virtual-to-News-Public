import random

from loguru import logger

from news.common.file_management import FileManagement
from news.common.folder_file import FolderFile
from news.common.handle_time import TakeTime
# from extract.util import filter,ranking,Vectorizer,sentence_delimiters
from news.extract import util


class Extract():
    def __init__(
            self,
            topic: str,
            sentence_delimiters: list = util.sentence_delimiters,
            article_list: list = [],
            source_path: str = './assets/json',
            destination_path: str = './assets',
            end_date: str = TakeTime.now_datetime(),
            date_duration: int = 7,
            classification_mode: str = 'keywords',  # 'nouns_ner' None
            source_exclude: list = []  # 'aune'
    ):
        self.topic = topic
        self.sentence_delimiters = sentence_delimiters
        self.end_date = end_date
        self.date_duration = date_duration
        if source_path is not None and not article_list:
            file_list = FolderFile(
                source_path=source_path,
                end_date=end_date,
                date_duration=date_duration).get_file_path_list()
            article_list = FileManagement.according_to_target(
                file_list, topic, classification_mode, source_exclude)
            logger.info(f"幾篇：{len(article_list)}")
        self.destination_path = destination_path
        self.article_lsit = article_list

    def extract(self, shuffle: bool = False, n_sentences: int = 0, filename: str = None):
        article_list = self.article_lsit
        topic = self.topic
        sentence_list = util.Filter.all(article_list, self.sentence_delimiters,
                                        topic)
        logger.info(f"幾句：{len(sentence_list)}")
        if shuffle:
            random.shuffle(sentence_list)
        generate_quantity = int(len(sentence_list)**0.5)
        sentence_list.insert(0, topic)
        vectors = util.Vectorizer.bert_many_sentences(sentence_list,
                                                      vectors=[],
                                                      batch=500,
                                                      vector_num=0)
        sentences_rank_top = util.ranking(vectors[0], vectors[1:],
                                          generate_quantity, sentence_list[1:])
        first = topic
        if not n_sentences:
            n_sentences = int(generate_quantity / 2)
        elif n_sentences > generate_quantity:
            logger.error("Want to output more sentences than original sentences.")
            logger.warning("Start preset output.")
            n_sentences = int(generate_quantity / 2)

        content = util.Vectorizer.sentences_combination(
            sentences=sentences_rank_top,
            first=first,
            few_sentences=n_sentences)

        content = util.Filter.content_conversion(content)
        destination_path = self.destination_path
        if filename is None:
            filename = topic + self.end_date + '-day' + str(
                self.date_duration) + '.txt'
        content = '主題是' + topic + '。\n' + content
        FileManagement.save_extract(filename=filename,
                                    destination_path=destination_path,
                                    content=content)
        return content


if __name__ == "__main__":
    topic = '疫苗'
    end_date = '2022-06-27'
    source_path = './assets/json'
    article_extract = Extract(topic=topic,
                              source_path=source_path,
                              end_date=end_date)
    article_extract.extract(shuffle=True)
