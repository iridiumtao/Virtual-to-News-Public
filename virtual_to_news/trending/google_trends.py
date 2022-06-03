import pandas as pd
from pytrends.request import TrendReq
from loguru import logger
import time
from enum import Enum


class GoogleTrends:
    class Tournament(Enum):
        CHAMPION = 1
        FINAL = 5
        SEMI_FINAL = 25
        QUARTER_FINAL = 225

    is_first_time = True

    def __init__(self,
                 keywords: list,
                 keep_duplicated_keywords_only,
                 tournament: Tournament = Tournament.FINAL,
                 category: int = 0,
                 timeframe_by_hour: bool = True,
                 timeframe: str = None):
        """
        透過 google trends 比較出本周最熱門的關鍵字 。
        未處理過的大量關鍵字可以透過 keep_duplicated_keywords_only，
        將未重複出現的關鍵字篩選掉，以減少 api request 次數。
        被 TrendingKeyword() 使用。

        :param keywords: 關鍵字
        :type keywords: list of str
        :param keep_duplicated_keywords_only: 決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析
        :type keep_duplicated_keywords_only: bool
        :param tournament: 欲取得的最熱門關鍵字數量（1~5）
        :type tournament: Tournament
        """
        self.keywords = keywords
        self.keep_duplicated_keywords_only = keep_duplicated_keywords_only
        logger.info(f"Keep duplicated keywords only: {keep_duplicated_keywords_only}")

        self.tournament = tournament
        logger.info(f"tournament: {tournament.name}")

        self.category = category
        logger.info(f"Category: {category}")

        if timeframe is not None:
            self.timeframe = timeframe
        else:
            self.timeframe = 'now 7-d' if timeframe_by_hour else 'today 1-m'

        logger.info(f"Timeframe: {self.timeframe}.")

    def top_trend(self):
        _keywords = self.duplicated_keywords_handler(self.keywords, self.keep_duplicated_keywords_only)

        while len(_keywords) > self.tournament.value:
            logger.info(f"Processed keywords {len(_keywords)}.")

            chunks = self.split_dataframe(_keywords)
            _keywords = self.chunk_looper(chunks)

            logger.info("----------------------------------------")
            logger.info(f"Keywords: {str(_keywords)}")
            logger.info("----------------------------------------")

        return _keywords

    @staticmethod
    def duplicated_keywords_handler(keywords, keep_duplicated_keywords_only):
        """
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

        if keep_duplicated_keywords_only:
            kw_series = kw_series[kw_series.duplicated()]

        kw_series.drop_duplicates(keep="first", inplace=True)
        kw_series.reset_index(drop=True, inplace=True)

        return kw_series.tolist()

    @staticmethod
    def split_dataframe(df, chunk_size=5):
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

    def chunk_looper(self, chunks: list):
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
            result_series = self.trend_requestor(chunk)
            logger.opt(colors=True).trace(f"Chunk ({i}/{chunks_size}): <white>===========================</white>")
            for index, value in result_series.iteritems():
                logger.opt(colors=True).trace(
                    f"Chunk ({i}/{chunks_size}): <fg #EEE>{index:\u3000<10}{value:>5}</fg #EEE>")
            logger.opt(colors=True).trace(f"Chunk ({i}/{chunks_size}): <red>Max is {result_series.idxmax()}</red>")
            kw_list.append(result_series.idxmax())

        logger.trace(f"Chunk ({i}/{chunks_size}): ===========================")

        return kw_list

    def trend_requestor(self, proceed_keywords: list, sort: bool = False) -> pd.Series:
        pytrends = TrendReq(hl='zn-TW', tz=-480)

        if len(proceed_keywords) > 5:
            raise ValueError("length of keyword list must be less than 5.")

        try:
            pytrends.build_payload(proceed_keywords, cat=self.category, timeframe=self.timeframe, geo='TW', gprop='')
            df = pytrends.interest_over_time()
        except ConnectionError as e:
            # 好像不會如預期執行
            logger.warning("ConnectionError")
            logger.warning(str(e))
            logger.warning(str(e.__traceback__))
            time.sleep(60)

            # 這應該是一個糟糕的寫法
            pytrends.build_payload(proceed_keywords, cat=self.category, timeframe=self.timeframe, geo='TW', gprop='')
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
