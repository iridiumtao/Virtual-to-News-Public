import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from loguru import logger

from news.common.handle_time import TakeTime
from news.extract.article_extract import Extract
from news.keywords.article_keywords import Keywords
from news.transcript import transcript
from news.trending.google_trends import GoogleTrends
from news.trending.trending_keywords import TrendingKeyword

cli = typer.Typer(help="Virtual to News -- 將AI帶入你的生活。")


class KeywordMethod(str, Enum):
    # segmentation = "segmentation"
    keywords = "keywords"
    keywords_jieba = "keywords_jieba"
    noun_ner = "noun_ner"


mode_list = ["mode_a", "mode_b", "mode_c"]

keep_duplicated_keywords_only_desc = """
決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析，用以減少 api request 次數。
使用情境：
「True」，若輸入關鍵字為爬蟲後未處理的大量關鍵字(>100個)。
「False」，若輸入關鍵字為精確的少量關鍵字(<100個)。"""

tournament_desc = """(錦標賽) 回傳的最熱門關鍵字數量，
必須為 {CHAMPION|FINAL|SEMI_FINAL|QUARTER_FINAL}。
CHAMPION: 回傳1個關鍵字。
FINAL: 回傳進入決賽關鍵字，1~5個。
SEMI_FINAL: 回傳進入半決賽關鍵字，6~25個。
QUARTER_FINAL: 回傳進入四分之一決賽關鍵字，26~225個。
預設為 FINAL"""

classification_mode_desc = """選取文章方法：
not_specify: 將所有新聞稿納入計算
appears: 將所有提及主題的新聞稿納入計算
輸入自選的 keyword_method: 尋找新聞稿中的keyword_method的list，如果其中包含主題，就將該篇新聞稿納入計算
"""


def tournament_checker(value: str):
    if value is None:
        return None

    if value.upper() in GoogleTrends.Tournament.__members__:
        return value
    else:
        raise typer.BadParameter(
            "Google Trends Tournament must be {CHAMPION|FINAL|SEMI_FINAL|QUARTER_FINAL}")


@cli.command()
def keywords(function: KeywordMethod = typer.Argument(..., help="選擇功能", case_sensitive=False),
             source_path: str = typer.Option('./assets/json', "--source-path", "-s", help="自訂輸入路徑"),
             destination_path: str = typer.Option('./assets/json',
                                                  "--destination-path",
                                                  "-d",
                                                  help="自訂輸出路徑"),
             has_title: bool = typer.Option(True, "--has-title/--no-title", help="是否把標題加入計算關鍵詞"),
             end_date: str = typer.Option(None, "--end-date", "-e", help="取的最後時間"),
             date_duration: int = typer.Option(7, "--date-duration", "-n", help="最後時間要往前取幾天"),
             skip_repetitive: bool = typer.Option(True,
                                                  "--skip-repetitive/--no-skip-repetitive",
                                                  help="是否要跳過重複類型的取關鍵字")):
    """
    關鍵詞提取。
    """
    if function.lower() in KeywordMethod.__members__:
        need_processed = function
    else:
        raise ValueError(f"does not have this function:{function.value}")

    Keywords.json_get_save(source_path=source_path,
                           destination_path=destination_path,
                           has_title=has_title,
                           end_date=end_date,
                           date_duration=date_duration,
                           skip_repetitive=skip_repetitive,
                           need_processed=[need_processed])
    logger.info("keywords finish")


@cli.command()
def trend(source_path: str = typer.Option(None, "--source-path", "-s", help="自訂輸入路徑及檔名"),
          keywords: List[str] = typer.Argument(None, help="設定關鍵字list"),
          end_date: str = typer.Option(None, "--end-date", "-e", help="熱度分析結束日期"),
          date_duration: int = typer.Option(None, "--date-duration", "-n", help="熱度分析的天數"),
          tournament: str = typer.Option(None,
                                         "--tournament",
                                         "-t",
                                         callback=tournament_checker,
                                         help=tournament_desc),
          category: int = typer.Option(0, help="Google Trends 的關鍵字類型。"),
          classification_mode: str = typer.Option('keywords', help="取檔模式")):
    """
    關鍵字流行比較，使用 Google Trends。

    注意請求次數過多會導致ResponseError 429，最好搭配代理伺服器使用。

    Google 用 AI 辨識機器人啦 怎麼解= =
    """
    if tournament is not None:
        _tournament = GoogleTrends.Tournament[tournament]
    else:
        raise typer.BadParameter(
            "Google Trends Tournament must be {CHAMPION|FINAL|SEMI_FINAL|QUARTER_FINAL}")

    if source_path is None and not keywords:
        raise typer.BadParameter("Source must be specified.")

    if end_date is None:
        end_date = TakeTime.now_datetime()
        logger.warning(f"end_date is not specified, using today's date ({end_date}) instead.")

    if date_duration is None:
        date_duration = 7
        logger.warning("date_duration is not specified, using 7 instead.")

    trkw = TrendingKeyword(end_date=end_date,
                           date_duration=date_duration,
                           source_path=source_path,
                           classification_mode=classification_mode,
                           keywords=keywords)

    trkw.filter_options(n_chars=1, n_times_in_articles=10, keyword_remove_words=True)

    kw = trkw.get_trending_keyword(filter=True, tournament=_tournament, category=category)
    logger.info(f"trending_keywords is {kw}")
    return kw


@cli.command()
def extract(
    topic: str = typer.Option(None, "--topic", "-t", help="選擇要取的主題"),
    source_path: str = typer.Option('./assets/json', "--source-path", "-s", help="自訂輸入路徑"),
    destination_path: str = typer.Option('./assets/article',
                                         "--destination-path",
                                         "-d",
                                         help="自訂輸出路徑"),
    end_date: str = typer.Option(None, "--end-date", "-e", help="取的最後時間"),
    date_duration: int = typer.Option(7, "--date-duration", "-n", help="最後時間要往前取幾天"),
    # sentence_delimiters: list = typer.Option(None,
    #                                          "--sentence-delimiters",
    #                                          help="最後時間要往前取幾天"),
    classification_mode: str = typer.Option('keywords',
                                            "--classification-mode",
                                            "-m",
                                            help=classification_mode_desc),
    n_sentences: int = typer.Option(0, "--n_sentences", "-ns", help="要取幾句"),
    # source_exclude: list = typer.Option(None,
    #                                     "--source-exclude",
    #                                     help="剔除哪家新聞網"),
    filename: str = typer.Option(None, "--filename", "-f", help="輸出檔案名稱")
):
    """
    文章提取。
    """
    article = None
    if topic is not None:
        article = Extract(topic=topic,
                          source_path=source_path,
                          destination_path=destination_path,
                          end_date=end_date,
                          date_duration=date_duration,
                          classification_mode=classification_mode).extract(shuffle=False,
                                                                           n_sentences=n_sentences,
                                                                           filename=filename)
        logger.info(f"extract is {article}")
    else:
        logger.info(f"extract is {article},because topic is {topic}.")
    return article


@cli.command()
def generate_news(function: KeywordMethod = typer.Argument(..., help="選擇功能", case_sensitive=False),
                  topic: str = typer.Option(None, "--topic", "-t", help="選擇要取的主題，如果有主題不會經過trend"),
                  source_path: str = typer.Option('./assets/json',
                                                  "--source-path",
                                                  "-s",
                                                  help="自訂輸入路徑"),
                  destination_path: str = typer.Option('./assets/article',
                                                       "-d",
                                                       "--destination-asset-path",
                                                       help="自訂輸出路徑"),
                  has_title: bool = typer.Option(True,
                                                 "--has-title/--no-title",
                                                 help="是否把標題加入計算關鍵詞"),
                  end_date: str = typer.Option(None, "--end-date", "-e", help="取的最後時間"),
                  date_duration: int = typer.Option(7, "--date-duration", "-n", help="最後時間要往前取幾天"),
                  skip_repetitive: bool = typer.Option(True,
                                                       "--skip-repetitive/--no-skip-repetitive",
                                                       help="是否要跳過重複類型的取關鍵字"),
                  category: int = typer.Option(7, help="Google Trends 的關鍵字類型。"),
                  n_sentences: int = typer.Option(0, "--n_sentences", "-ns", help="要取幾句"),
                  filename: str = typer.Option(None, "--filename", "-f", help="輸出檔案名稱")):
    """
    新聞處理的pipeline。一鍵執行提取關鍵字、流行關鍵字、文章提取。
    """

    if function is None:
        raise ValueError("keyword_method must be specified")
    logger.info(f"keyword_method: {function}")
    logger.info(f"source_path: {source_path}")
    logger.info(f"destination_asset_path: {destination_path}")
    logger.info(f"has_title: {has_title}")

    if end_date is None:
        end_date = TakeTime.now_datetime()
        logger.warning("end_date is not specified, using today's date instead.")
    logger.info(f"end_date: {end_date}")
    logger.info(f"date_duration: {date_duration}")
    logger.info(f"skip_repetitive: {skip_repetitive}")
    logger.info(f"category: {category}")

    # keywords_destination_path = destination_path + '/json'
    # extract_destination_path = destination_path + '/article'
    need_processed = ''

    if function.lower() in KeywordMethod.__members__:
        need_processed = function.value
    else:
        raise ValueError(f"does not have this function:{function.value}")
    keywords(function=need_processed,
             source_path=source_path,
             destination_path=source_path,
             has_title=has_title,
             end_date=end_date,
             date_duration=date_duration,
             skip_repetitive=skip_repetitive)

    if topic is None:
        tournament = GoogleTrends.Tournament.CHAMPION.name
        trend_defaults = trend.__defaults__
        keywords_defaults = trend_defaults[2]
        defualt_from_trend_argument = keywords_defaults.default
        trend_keywords = trend(source_path=source_path,
                               end_date=end_date,
                               date_duration=date_duration,
                               keywords=defualt_from_trend_argument,
                               tournament=tournament,
                               category=category,
                               classification_mode=need_processed)
        if isinstance(trend_keywords, list) and trend_keywords != []:
            topic = trend_keywords[0]
        elif isinstance(trend_keywords, str):
            topic = trend_keywords
        else:
            topic = None

    logger.info(f"topic: {topic}")
    if topic is not None:
        article = extract(topic=topic,
                          source_path=source_path,
                          destination_path=destination_path,
                          end_date=end_date,
                          date_duration=date_duration,
                          classification_mode=need_processed,
                          n_sentences=n_sentences,
                          filename=filename)
    else:
        logger.error('no topic')
        article = ''
    return article


@cli.command()
def get_transcript(article: str = typer.Option(None, "--article", "-a", help="需要處理的文章"),
                   num: int = typer.Option(10, "--num", "-n", help="照幾個字分句"),
                   filename: int = typer.Option('transcript.txt', "--filename", "-f", help="檔案名稱"),
                   destination_path: int = typer.Option('./assets/article',
                                                        "-d",
                                                        "--destination-asset-path",
                                                        help="檔案位置")):
    content = transcript(
            article=article,
            num=num,
            #  filename=topic + 'speech' + end_date + 'day' + str(date_duration) +
            #  '.txt',
            filename=filename,
            destination_path=destination_path)
    return content


if __name__ == "__main__":
    # 移除內建預設 logger
    logger.remove()

    # 加入寫檔logger
    logger.add("log/news.log", rotation="100 KB", level="TRACE", backtrace=True, diagnose=True)

    # 加入顯示在 terminal 的自定義 logger
    logger.add(sys.stdout, level="TRACE", backtrace=True, diagnose=True)
    cli()
