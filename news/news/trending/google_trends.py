import time
from enum import Enum
from random import uniform

import pandas as pd
from loguru import logger
from pytrends.exceptions import ResponseError
# from pytrends.request import TrendReq
from pytrends.request import TrendReq as UTrendReq

from news.common.agent import headers
# import random
# import requests
# from requests.packages import urllib3
# urllib3.disable_warnings()
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

GET_METHOD = 'get'
os.environ['NO_PROXY'] = 'trends.google.com'


def get_proxies():
    file_path = './assets/proxy.csv'
    proxys_df = pd.read_csv(file_path)['proxy']
    return list(proxys_df)


class TrendReq(UTrendReq):
#     def __init__(self,
#                  hl='en-US',
#                  tz=360,
#                  geo='',
#                  timeout=(2, 5),
#                  proxies='',
#                  retries=0,
#                  backoff_factor=0,
#                  requests_args=None):

#         # proxies = RandomProxy('./news/crawlers/proxy.json')
#         # proxies = RandomProxy.process_request(proxies.proxies)
#         # proxies = RandomProxy('./news/crawlers/proxy.json').proxies['https']
#         # proxies = get_proxies()
#         return super().__init__(hl=hl,
#                                 tz=tz,
#                                 geo=geo,
#                                 timeout=timeout,
#                                 proxies=proxies,
#                                 retries=retries,
#                                 backoff_factor=backoff_factor,
#                                 requests_args=requests_args)

#     def GetGoogleCookie(self):
#         """
#         Gets google cookie (used for each and every proxy; once on init otherwise)
#         Removes proxy from the list on proxy error
#         """
#         while True:
#             if "proxies" in self.requests_args:
#                 try:
#                     return dict(
#                         filter(
#                             lambda i: i[0] == 'NID',
#                             requests.get(
#                                 'http://trends.google.com/?geo={geo}'.format(
#                                     geo=self.hl[-2:]),
#                                 timeout=self.timeout,
#                                 **self.requests_args).cookies.items()))
#                 except:
#                     continue
#             else:
#                 if len(self.proxies) > 0 and self.proxies != '':
#                     # self.GetNewProxy()
#                     # self.proxy_index = random.randrange(len(self.proxies))
#                     # proxy = {'https': self.proxies[self.proxy_index]}
#                     proxy = {'http': self.proxies[self.proxy_index]}
#                     # print(self.proxy_index, proxy)
#                 else:
#                     proxy = ''
#                 try:
#                     response = requests.get(
#                         'http://trends.google.com/?geo={geo}'.format(
#                             geo=self.hl[-2:]),
#                         timeout=self.timeout,
#                         proxies=proxy,
#                         **self.requests_args)
#                     response_dict = dict(
#                         filter(lambda i: i[0] == 'NID',
#                                response.cookies.items()))
#                     response.close()
#                     return response_dict
#                 except requests.exceptions.ProxyError:
#                     # print('Proxy error. Changing IP')
#                     if len(self.proxies) > 1:
#                         # print('Proxy error', self.proxies[self.proxy_index])
#                         self.proxies.remove(self.proxies[self.proxy_index])
#                     else:
#                         print('No more proxies available. Bye!')
#                         raise
#                     continue
#                 except requests.exceptions.ConnectTimeout:
#                     # print('ConnectTimeout')
#                     if len(self.proxies) > 1:
#                         # print('ConnectTimeout', self.proxies[self.proxy_index])
#                         self.proxies.remove(self.proxies[self.proxy_index])
#                     else:
#                         print('No more proxies available. Bye!')
#                         raise
#                     continue
#                 except requests.exceptions.ReadTimeout:
#                     # print('ReadTimeout')
#                     if len(self.proxies) > 1:
#                         # print('ReadTimeout', self.proxies[self.proxy_index])
#                         self.proxies.remove(self.proxies[self.proxy_index])
#                     else:
#                         print('No more proxies available. Bye!')
#                         raise
#                     continue

#     def GetNewProxy(self):
#         """
#         Increment proxy INDEX; zero on overflow
#         """
#         if len(self.proxies) > 0:
#             self.proxy_index = random.randrange(len(self.proxies))
#         # if self.proxy_index < (len(self.proxies) - 1):
#         #     self.proxy_index += 1
#         # else:
#         #     self.proxy_index = 0

    def _get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
        h = headers()
        return super()._get_data(url,
                                 method=method,
                                 trim_chars=trim_chars,
                                 headers=h,
                                 **kwargs)


class GoogleTrends:
    '''
    透過 google trends 比較出本周最熱門的關鍵字。
    被 TrendingKeyword() 使用。
    負責：利用 pytrends 跟 Google trends 打交道、執行淘汰賽

    ## 使用方法：

    輸入關鍵字
    ```
    keywords = [...] # 一個經過處理(不重複、沒有垃圾)的關鍵詞列表

    ```

    初始化 GoogleTrends
    其他參數見 trending_keywords.py
    ```
    trend = GoogleTrends(keywords,
                         tournament=tournament,
                         category=category,
                         timeframe=timeframe)
    ```

    取得最熱門關鍵字
    ```
    top_trend = trend.top_trend()
    ```
    '''
    class Tournament(Enum):
        CHAMPION = 1
        FINAL = 5
        SEMI_FINAL = 25
        QUARTER_FINAL = 225

    is_first_time = True

    def __init__(self,
                 keywords: list,
                 keep_duplicated_keywords_only,
                 timeframe: str,
                 tournament: Tournament = Tournament.FINAL,
                 category: int = 0):
        """

        :param keywords: 關鍵字
        :type keywords: list of str
        :param keep_duplicated_keywords_only: deprecarted 決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析
        :type keep_duplicated_keywords_only: bool
        :param tournament: 欲取得的最熱門關鍵字數量（1~5）
        :type tournament: Tournament
        """
        self.keywords = keywords
        self.keep_duplicated_keywords_only = keep_duplicated_keywords_only
        logger.info(
            f"Keep duplicated keywords only: {keep_duplicated_keywords_only}")

        self.tournament = tournament
        logger.info(f"tournament: {tournament.name}")

        self.category = category
        logger.info(f"Category: {category}")

        self.timeframe = timeframe

        logger.info(f"Timeframe: {self.timeframe}.")

    def top_trend(self):
        '''
        取得最熱門關鍵字

        :return: 關鍵字 list
        :rtype: list
        '''

        # 此方法已棄用
        # _keywords = self._duplicated_keywords_handler(
        #     self.keywords, self.keep_duplicated_keywords_only)
        _keywords = self.keywords

        while len(_keywords) > self.tournament.value:
            logger.info(f"Processed keywords {len(_keywords)}.")

            chunks = self._split_dataframe(_keywords)
            _keywords = self._chunk_looper(chunks)

            logger.info("----------------------------------------")
            logger.info(f"Keywords: {str(_keywords)}")
            logger.info("----------------------------------------")

        return _keywords

    @staticmethod
    def _duplicated_keywords_handler(keywords, keep_duplicated_keywords_only):
        """
        # Deprecated
        ### 現在使用 TrendingKeyword._filter_keywords() 來實作

        將重複的關鍵字去除

        :param keywords: 輸入 list of keywords
        :type keywords: list
        :param keep_duplicated_keywords_only: 決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析
        :type keep_duplicated_keywords_only: bool
        :return: 處理過的 list of keywords
        :rtype: list
        """
        logger.info(f"Unprocessed keywords: {len(keywords)}.")
        kw_series = pd.Series(keywords)

        # todo: 這邊改成使用keywords_filter
        if keep_duplicated_keywords_only:
            kw_series = kw_series[kw_series.duplicated()]

        kw_series.drop_duplicates(keep="first", inplace=True)
        kw_series.reset_index(drop=True, inplace=True)

        return kw_series.tolist()

    @staticmethod
    def _split_dataframe(df, chunk_size=5):
        """
        Splits the DataFrame into smaller chunks

        :param df: a Dataframe (or list)
        :type df: pd.DataFrame or list
        :param chunk_size: the length of dataframe that you want to split
        :type chunk_size: int
        :return: list of dataframe or list
        :rtype: list
        """
        size_df = len(df)

        if size_df < chunk_size:
            logger.warning("df size is smaller than chunk_size.")
            logger.info(f"size_df = {size_df}, chunk_size = {chunk_size}")
            return [df]

        chunks = list()

        # Fancy way 的無條件進位法
        num_chunks = -(-size_df // chunk_size)
        logger.info(f"Split into {num_chunks} chunks.")

        for i in range(num_chunks):
            chunks.append(df[i * chunk_size:(i + 1) * chunk_size])

        return chunks

    def _chunk_looper(self, chunks: list):
        """
        將 chunks 逐一執行 trend_requestor()

        :param chunks: 切小塊的 list
        :type chunks: list
        :return: list of keywords
        :rtype: list
        """
        kw_list = []

        chunks_size = len(chunks)
        logger.trace(f"Chunks_size: {chunks_size}")
        logger.trace(f"Chunks: {str(chunks)}")

        i = 0
        for chunk in chunks:
            i += 1
            result_series = self._trend_requestor(chunk)
            logger.opt(colors=True).trace(
                f"Chunk ({i}/{chunks_size}): <white>===========================</white>"
            )
            for index, value in result_series.iteritems():
                logger.opt(colors=True).trace(
                    f"Chunk ({i}/{chunks_size}): <fg #EEE>{index:\u3000<10}{value:>5}</fg #EEE>"
                )
            logger.opt(colors=True).trace(
                f"Chunk ({i}/{chunks_size}): <red>Max is {result_series.idxmax()}</red>"
            )
            kw_list.append(result_series.idxmax())

        logger.trace(f"Chunk ({i}/{chunks_size}): ===========================")

        return kw_list

    # def _response_error_b(self, proceed_keywords, cat, timeframe, geo, gprop):
    #     try:
    #         time.sleep(uniform(1, 2))
    #         self.pytrends.build_payload(proceed_keywords,
    #                                     cat=cat,
    #                                     timeframe=timeframe,
    #                                     geo=geo,
    #                                     gprop=gprop)
    #         # return self.pytrends
    #     except ResponseError as e:
    #         # logger.warning("ConnectionError")
    #         # logger.warning(str(e))
    #         # logger.warning(str(e.__traceback__))
    #         time.sleep(1)
    #         self._response_error_b(proceed_keywords, cat, timeframe, geo,
    #                                gprop)
    #     except requests.exceptions as ex:
    #         # logger.warning("ConnectionError")
    #         # logger.warning(str(ex))
    #         # logger.warning(str(ex.__traceback__))
    #         time.sleep(1)
    #         self._response_error_b(proceed_keywords, cat, timeframe, geo,
    #                                gprop)

    # def _response_error_i(self):
    #     try:
    #         time.sleep(uniform(1, 2))
    #         self.df = self.pytrends.interest_over_time()
    #         # return df
    #     except ResponseError as e:
    #         # logger.warning("ConnectionError")
    #         # logger.warning(str(e))
    #         # logger.warning(str(e.__traceback__))
    #         time.sleep(1)
    #         self._response_error_i()

    def _trend_requestor(self,
                         proceed_keywords: list,
                         sort: bool = False) -> pd.Series:
        pytrends = TrendReq(hl='zn-TW', tz=-480)

        if len(proceed_keywords) > 5:
            raise ValueError("length of keyword list must be less than 5.")
        # pytrends = self._response_error_b(pytrends,
        #                                   proceed_keywords,
        #                                   cat=self.category,
        #                                   timeframe=self.timeframe,
        #                                   geo='TW',
        #                                   gprop='')
        # if pytrends == None:
        #     pytrends = TrendReq(hl='zn-TW', tz=-480)
        #     pytrends = self._response_error_b(pytrends,
        #                                       proceed_keywords,
        #                                       cat=self.category,
        #                                       timeframe=self.timeframe,
        #                                       geo='TW',
        #                                       gprop='')

        # df = self._response_error_i(pytrends)
        # if (df.empty):
        #     df = self._response_error_i(pytrends)
        try:
            time.sleep(uniform(2, 5))
            pytrends.build_payload(proceed_keywords,
                                   cat=self.category,
                                   timeframe=self.timeframe,
                                   geo='TW',
                                   gprop='')
            df = pytrends.interest_over_time()
        except ResponseError as e:
            # 好像不會如預期執行
            logger.warning("ConnectionError")
            logger.warning(str(e))
            logger.warning(str(e.__traceback__))
            time.sleep(20)

            # 這應該是一個糟糕的寫法
            pytrends.build_payload(proceed_keywords,
                                   cat=self.category,
                                   timeframe=self.timeframe,
                                   geo='TW',
                                   gprop='')
            df = pytrends.interest_over_time()

        # 依照日期排序
        df.sort_values("date", ascending=False, inplace=True)

        # 刪除統計未完整資料
        # 只保留 isPartial 為 False 的
        # 通常刪除最近一天的資料
        df = df.loc[(df['isPartial'] == False)]

        # 取近七天的資訊
        if self.timeframe != "now 7-d":
            df = df[:7]

        if self.is_first_time:
            logger.trace("First DataFrame:")
            logger.opt(raw=True).trace(df)
            logger.opt(raw=True).trace("\n")
            self.is_first_time = False

        # 加總（type 會變成 Series）
        ranking_series = df.sum()

        # 刪除不需要的欄位
        ranking_series.drop('isPartial', inplace=True)

        if sort:
            ranking_series.sort_values(ascending=False, inplace=True)

        return ranking_series
