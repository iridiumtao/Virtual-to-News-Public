import random
import sys
from pathlib import Path

import pandas as pd
from loguru import logger

from news.common.file_management import FileManagement
from news.common.folder_file import FolderFile
from news.common.handle_time import TakeTime
from news.trending.google_trends import GoogleTrends

# 移除內建預設 logger
logger.remove()

# 加入寫檔logger
logger.add("google_trends.log",
           rotation="100 KB",
           level="TRACE",
           backtrace=True,
           diagnose=True)

# 加入顯示在 terminal 的自定義 logger
logger.add(sys.stdout, level="TRACE", backtrace=True, diagnose=True)


class TrendingKeyword:
    """
    找出最熱門關鍵字。
    作為 GoogleTrends() 的前處理。
    負責：讀入關鍵字列表、篩選關鍵字，去蕪存菁

    ## 使用方法：
    先 init 此 class
    如果要讀取已儲存的新聞稿來取得關鍵字：
    ```
    trkw = trending_keywords.TrendingKeyword(
        end_date="2022-11-05",
        date_duration=7
        source_path="path/to/news"
    )
    ```

    如果要直接輸入關鍵字：
    ```
    keywords = [...] # A list of 關鍵字

    trkw = trending_keywords.TrendingKeyword(
        end_date="2022-11-05",
        date_duration=7
        keywords=keywords
    )
    ```

    接著設定關鍵字過濾選項
    ```
    trkw.filter_options(n_chars=1,
                        n_times_in_articles=5,
                        keywords=True)
    ```

    最後啟動流行趨勢分析程式（回傳關鍵字的list）
    ```
    keywords = trkw.get_trending_keyword(
        tournament=GoogleTrends.Tournament.FINAL,
        category=0
    )
    ```

    """
    json_path = None
    timeframe = None


    def __init__(self,
                 end_date: str,
                 date_duration: int,
                 source_path: str = './assets/json',
                 keywords: list = None,
                 classification_mode: str = 'keywords',
                 source_exclude: list = []):
        """
        關鍵字的路徑或直接傳入 list of 關鍵字

        :param json_path: 就路徑，依照 @sloth-eat-pudding 定義的格式
        :type json_path: str, Path
        :param keywords: a list of 關鍵字
        :type keywords: list
        """
        logger.trace("This is a new instance of TrendingKeyword.")

        # 如果未輸入 keywords 或是 keywords 數量為 0
        if keywords is None or len(keywords) == 0:
            # 從檔案中讀取關鍵字
            file_list = FolderFile(
                source_path=source_path,
                end_date=end_date,
                date_duration=date_duration).get_file_path_list()

            # 避免與 param 的 keywords 混淆
            _keywords = FileManagement.get_keywords(file_list,
                                                    classification_mode,
                                                    source_exclude)
            self.keywords = _keywords
        else:
            self.keywords = keywords

        # TODO: 現在這邊一團混亂
        self.star_date = end_date
        end_year, end_month, end_day = TakeTime.take_need_day(
            end_date, date_duration)
        self.end_date = end_year + '-' + end_month + '-' + end_day
        self.timeframe = self.end_date + ' ' + end_date

    def filter_options(self,
                       n_chars: int = 1,
                       n_times_in_articles: int = 10,
                       keyword_remove_words: bool = False):
        """
        關鍵字過濾選項
        :param n_chars: 決定一個關鍵字的字數應大於幾 i.e. 只保留字數大於n的關鍵字
        :type n_chars: int
        :param n_times_in_articles: 決定關鍵字須出現在幾篇文章中
        :type n_times_in_articles: int
        :param keyword_remove_words: 是否移除符合「關鍵字刪除詞表」內的詞彙
        :type keyword_remove_words: bool
        """
        self.n_chars = n_chars
        self.n_times_in_articles = n_times_in_articles
        self.keyword_remove_words = keyword_remove_words

    @logger.catch
    def get_trending_keyword(self,
                             filter: bool = True,
                             tournament: GoogleTrends.
                             Tournament = GoogleTrends.Tournament.FINAL,
                             category: int = 0):
        """
        用來啟動 GoogleTrends 的 function

        :param filter: 使用關鍵字過濾器(預設：True)
        :type filter: bool
        :type keep_duplicated_keywords_only: bool
        :param tournament: (錦標賽) 回傳的最熱門關鍵字數量，
                CHAMPION: 回傳1個關鍵字。
                FINAL: 回傳進入決賽關鍵字，1~5個。
                SEMI_FINAL: 回傳進入半決賽關鍵字，6~25個。
                QUARTER_FINAL: 回傳進入四分之一決賽關鍵字，26~225個。
                預設為 GoogleTrends.Tournament.FINAL
        :type tournament: GoogleTrends.Tournament
        :param category: Google Trends 的關鍵字類型。
                預設為0（全部類型），其他可能會用的標籤：Finance: 7, Business Finance: 1138, Financial Markets: 1163。
                參見：https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories
        :type category: int
        """

        # 檢查關鍵字有被設定
        if not isinstance(self.keywords, list):
            raise ValueError("Keywords must be specified.")

        if filter:
            # 檢查 filter_options 有被設定
            if (self.n_chars and self.n_times_in_articles
                    and self.keyword_remove_words) is None:
                raise ValueError(
                    "filter_options() 未被設定。請在執行 get_trending_keyword() 前調動該方法")

            self._filter_keywords(self.keywords)

        random.shuffle(self.keywords)

        if self.timeframe is not None:
            timeframe = self.timeframe

        trend = GoogleTrends(self.keywords,
                             keep_duplicated_keywords_only=False,
                             tournament=tournament,
                             category=category,
                             timeframe=timeframe)
        top_trend = trend.top_trend()
        return top_trend

    def _filter_keywords(self, keywords):
        """
        使用預設選項過濾關鍵字
        n_chars: int = 1
        n_times_in_articles: int = 10
        keyword_remove_words: bool = False
        """

        # TODO: 註解請求
        word_dict = {}
        not_word_dict = {}
        for keyword in keywords:
            if keyword not in not_word_dict.keys() and keyword not in word_dict.keys() and len(keyword) > self.n_chars:
                keywords_count = keywords.count(keyword)
                if keywords_count > self.n_times_in_articles:
                    word_dict[keyword] = keywords_count
                else:
                    not_word_dict[keyword] = keywords_count

        keywords = list(word_dict.keys())
        if self.keyword_remove_words:

            # 關鍵字刪除詞表的路徑
            filepath = Path() / "assets" / "keywords_remove_words.txt"
            file = Path.open(filepath, encoding='utf-8')
            remove_keywords = file.readlines()

            # Strips the newline character
            for r_keyword in remove_keywords:
                if r_keyword.strip() in keywords:
                    keywords.remove(r_keyword.strip())
        self.keywords = keywords

    @staticmethod
    def list_of_lists_to_list(data):
        """將[..., ..., ...], ..., [..., ..., ...] 轉換為 [..., ..., ..., ... ..., ..., ...]"""
        return [element for list_ in data for element in list_]

    @staticmethod
    @logger.catch
    def read_time(database):
        """測試用
        利用 pandas 內建的 Timestamp 來印出時間，這樣就可以不用 import datetime (?)"""

        # 使用第一篇文章的時間戳
        # todo 可能需要調整
        timestamp = database["date"][0]

        ts = pd.Timestamp(timestamp, unit='s', tz='Asia/Taipei')
        print(ts.strftime('%Y-%m-%d'))

        ts2 = ts - pd.Timedelta(days=7)
        print(ts2.strftime('%Y-%m-%d'))
        '''YYYY-MM-DD YYYY-MM-DD'''
        return f"{ts2.strftime('%Y-%m-%d')} {ts.strftime('%Y-%m-%d')}"


# 測試用
if __name__ == "__main__":
    keywords = [
        '疫苗', '平台', '月', '科技', '價格', '電信', '台積電', '城', '股價', '資訊', '交易', '股票',
        '基金', '政策', '特斯拉', '社交', '國家', '汽車', '美元', '電子', '稅', '房', '股東', '油價',
        '房子', '車', '卡', '高鐵'
    ]
    tk = TrendingKeyword(keywords=keywords)
    tk = TrendingKeyword(
        json_path="../../assets/json/keyword/test3333_keyword.json",
        read_date_in_json=True)
    result = tk.get_trending_keyword(filter=True,
                                     tournament=GoogleTrends.Tournament.FINAL,
                                     category=7,
                                     timeframe_by_hour=True)
    print(result)
