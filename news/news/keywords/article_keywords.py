from tqdm import tqdm
from loguru import logger

from news.common.file_management import FileManagement
from news.common.folder_file import FolderFile
from news.common.handle_time import TakeTime
from news.keywords.article_analyzer import ArticleAnalyzer


class Keywords():
    def __init__():
        pass

    def json_get_save(source_path: str = './assets/json',
                      has_title: bool = True,
                      destination_path: str = './assets/json',
                      date_duration: int = 0,
                      end_date: str = TakeTime.now_datetime(),
                      skip_repetitive: bool = True,
                      need_processed: list = ['keywords']):
        file_path_list = FolderFile(
            source_path=source_path,
            end_date=end_date,
            date_duration=date_duration).get_file_path_list()
        file_path_list_tqdm = tqdm(file_path_list)
        for file_path in file_path_list_tqdm:
            file_path_list_tqdm.set_description('Process articles %s' %
                                                file_path)
        # for file_path in file_path_list:
            # logger.info("Process articles {}", file_path)
            # 使用過的方法要不要再提取一次
            if skip_repetitive:
                processed = ArticleAnalyzer.need_processed(
                    file_path, need_processed)
            else:
                processed = need_processed

            save_path = file_path.replace(source_path, destination_path)
            file = FileManagement(source_path=file_path)
            file.to_articles(has_title=has_title)

            article_analyzer = ArticleAnalyzer(content_list=file.contents)
            if 'keywords' in processed:
                file.get_data()
                article_analyzer.nouns_ner = file.nouns_ner
                article_analyzer.contents_word_segmenter = file.contents_word_segmenter
                article_analyzer.contents_pos_tagger = file.contents_pos_tagger
                article_analyzer.get_keywords(ner=True)

                file.nouns_ner = article_analyzer.nouns_ner
                file.keywords = article_analyzer.keywords  # textrank+idf 有篩選(數字比例多、排序前五)
                file.keywords_t = article_analyzer.keywords_t  # only textrank 有篩選(數字比例多、排序前五)
                file.contents_word_segmenter = article_analyzer.contents_word_segmenter
                file.contents_pos_tagger = article_analyzer.contents_pos_tagger
                # file.contents_no_filter=article_analyzer.contents_no_filter
                # file.contents_no_stop_words=article_analyzer.contents_no_stop_words
                file.contents_all_filters = article_analyzer.contents_all_filters
                # file.contents_numerical_value=article_analyzer.contents_numerical_value
                # file.textrank_weights=article_analyzer.textrank_weights
                # file.weights=article_analyzer.weights

            if 'keywords_jieba' in processed:
                # file.keywords_jieba = article_analyzer.get_keywords_jieba()
                keywords_jieba = article_analyzer.get_keywords_jieba()
                file.keywords_jieba = keywords_jieba
            if 'nouns_ner' in processed:
                # file.nouns_ner = article_analyzer.get_nouns_ner()
                nouns_ner = article_analyzer.get_nouns_ner()
                file.nouns_ner = nouns_ner
            # if 'nouns_pipeline' in processed:
            #     # file.nouns_pipeline = article_analyzer.get_nouns_pipeline()
            #     nouns_pipeline = article_analyzer.get_nouns_pipeline()
            #     file.nouns_pipeline=nouns_pipeline

            file.save_all_exists(source_path=file_path,
                                 destination_path=save_path)

    # def article_get(title: str = None,
    #                 content: str = None,
    #                 has_title: bool = False,
    #                 need_processed: list = ['keywords']
    #                 ):
    #     articles_list = ArticleAnalyzer(
    #         title=title, content=content, has_title=has_title)

    #     keywords = None
    #     keywords_jieba = None
    #     nouns_pipeline = None
    #     nouns_ner = None

    #     if 'keywords' in need_processed:
    #         keywords = articles_list.get_keywords()
    #     if 'keywords_jieba' in need_processed:
    #         keywords_jieba = articles_list.get_keywords_jieba()
    #     if 'nouns_ner' in need_processed:
    #         nouns_ner = articles_list.get_nouns_ner()
    #     if 'nouns_pipeline' in need_processed:
    #         nouns_pipeline = articles_list.get_nouns_pipeline()
    #     return keywords, keywords_jieba, nouns_pipeline, nouns_ner


if __name__ == "__main__":
    # need_processed = ['keywords', 'keywords_jieba', 'nouns_ner']
    # need_processed = ['nouns_pipeline']
    need_processed = ['keywords']
    Keywords.json_get_save(skip_repetitive=True,
                           need_processed=need_processed,
                           end_date='2022-06-27',
                           date_duration=0)

    # title = "台歐盟深化離岸風電合作 經部估今年可完成逾200支風機安裝"
    # content = "經濟部今 (21) 日表示，近期與歐洲經貿辦事處、歐盟會員國駐台辦事處，舉辦第二次台灣 - 歐盟離岸風電會議，深化離岸風電雙邊合作，經濟部也預期，台灣今年底將完成安裝 200 支以上離岸風機，可望進一步促進與國外風電業者的緊密合作，提升我國離岸風電人才、供應鏈在亞洲離岸風電市場地位。\n為強化台歐盟離岸風電交流，經濟部與歐洲經貿辦事處成立台歐盟離岸風電小組，在今年 3 月 2 日已召開第一次台歐盟離岸風電小組會議，近日再舉辦第二次台灣 - 歐盟離岸風電會議，由經濟部長王美花、歐盟輪值主席法國在台協會主任公孫孟共同主持。\n經濟部指出，本次會議，雙方聚焦在施工中風場的防疫規範及緊急醫療措施、第三階段區塊開發選商機制、浮動式風電在台灣的發展策略等，針對歐盟關切第三階段區塊開發，已與各國及本土業者進行多次意見交換，對現階段選商規定多有共識，目前也已啟動研擬浮動式離岸風電計畫。\n經濟部表示，台灣與歐盟透過本次離岸風電平台會議，討論現階段遭遇議題、推動展望，將有助我國離岸風電進一步發展，也預期台灣今年底將完成安裝 200 支以上的離岸風機。\n\n"
    # Keywords.article_get(title=title,
    #                      content=content,
    #                      has_title=True,
    #                      need_processed=need_processed)
