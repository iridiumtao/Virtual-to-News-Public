import pandas as pd
from loguru import logger
import sys
from pytrends.request import TrendReq
import random

from .google_trends import GoogleTrends

# 移除內建預設 logger
logger.remove()

# 加入寫檔logger
logger.add("google_trends.log", rotation="100 KB", level="TRACE", backtrace=True, diagnose=True)

# 加入顯示在 terminal 的自定義 logger
logger.add(sys.stdout, level="TRACE", backtrace=True, diagnose=True)


class TrendingKeyword:
    """
    找出最熱門關鍵字所使用的 class。
    作為 GoogleTrends() 的前處理
    """
    json_path = None
    timeframe = None

    def __init__(self, json_path=None, keywords: list = None, read_date_in_json: bool = False):
        """
        關鍵字的路徑或直接傳入 list of 關鍵字

        :param json_path: 就路徑，依照 @sloth-eat-pudding 定義的格式
        :type json_path: str, Path
        :param keywords: a list of 關鍵字
        :type keywords: list
        """
        logger.warning("This is a new instance of TrendingKeyword.")
        if json_path is not None:
            # read json database
            database = pd.read_json(json_path)
            database = database.transpose()
            self.json_path = database

            # get keywords from database
            self.keywords = self.list_of_lists_to_list(database["noun_Pipeline"])

            if read_date_in_json:
                self.timeframe = self.read_time(database)
                logger.info("Read date in json is True.")

        elif isinstance(keywords, list):
            self.keywords = keywords

            if read_date_in_json is True:
                raise ValueError("Json path must be specified to read the date.")

        else:
            raise ValueError("Source must be specified.")

    @staticmethod
    @logger.catch
    def read_time(database):
        """利用 pandas 內建的 Timestamp 來印出時間，這樣就可以不用 import datetime (?)"""

        # 使用第一篇文章的時間戳
        # todo 可能需要調整
        timestamp = database["date"][0]

        ts = pd.Timestamp(timestamp, unit='s', tz='Asia/Taipei')
        print(ts.strftime('%Y-%m-%d'))

        ts2 = ts - pd.Timedelta(days=7)
        print(ts2.strftime('%Y-%m-%d'))

        '''YYYY-MM-DD YYYY-MM-DD'''
        return f"{ts2.strftime('%Y-%m-%d')} {ts.strftime('%Y-%m-%d')}"

    @logger.catch
    def get_trending_keyword(self,
                             keep_duplicated_keywords_only,
                             tournament: GoogleTrends.Tournament = GoogleTrends.Tournament.FINAL,
                             category: int = 0,
                             timeframe_by_hour: bool = True,
                             timeframe: str = None):
        """
        用來啟動 GoogleTrends 的 function

        :param keep_duplicated_keywords_only: 決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析，用以減少 api request 次數。
                使用情境：
                「True」，若輸入關鍵字為爬蟲後未處理的大量關鍵字(>100個)。
                「False」，若輸入關鍵字為精確的少量關鍵字(<100個)。
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
        :param timeframe_by_hour: 決定 api 抓取數值的時間區間與間隔。
                「True」則抓取最近7日每小時('now 7-d')，「False」則抓取最近1個月每天('today 1-m')。
                預設為「True」。
        :type timeframe_by_hour: bool
        :param timeframe: 用以手動調整 api 抓取數值的時間區間與間隔，
                預設為 None，使用 timeframe_by_hour 的設定。
                ⚠️注意：若非 'now 7-d'，會自動只保留前7項有效數據，因為本實作的目標為「找出一週流行關鍵字」
                參見：https://github.com/GeneralMills/pytrends#common-api-parameters 之 timeframe 說明
        :type timeframe: str
        """
        if not isinstance(self.keywords, list):
            raise ValueError("Keywords must be specified.")

        random.shuffle(self.keywords)

        if self.timeframe is not None:
            timeframe = self.timeframe

        trend = GoogleTrends(self.keywords,
                             keep_duplicated_keywords_only,
                             tournament=tournament,
                             category=category,
                             timeframe_by_hour=timeframe_by_hour,
                             timeframe=timeframe)
        top_trend = trend.top_trend()
        return top_trend

    @staticmethod
    def list_of_lists_to_list(data):
        """將[..., ..., ...], ..., [..., ..., ...] 轉換為 [..., ..., ..., ... ..., ..., ...]"""
        return [element for list_ in data for element in list_]


# 測試用
if __name__ == "__main__":
    keywords = ['疫苗', '平台', '月', '科技', '價格', '電信', '台積電', '城', '股價', '資訊', '交易', '股票', '基金', '政策', '特斯拉', '社交', '國家', '汽車', '美元', '電子', '稅', '房', '股東', '油價', '房子', '車', '卡', '高鐵']
    #tk = TrendingKeyword(keywords=keywords)
    tk = TrendingKeyword(json_path="../../assets/json/keyword/test3333_keyword.json", read_date_in_json=True)
    result = tk.get_trending_keyword(keep_duplicated_keywords_only=True, tournament=GoogleTrends.Tournament.FINAL, category=7, timeframe_by_hour=True)
    print(result)

