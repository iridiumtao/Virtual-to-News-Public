import typer
import sys
from typing import List, Optional
from pathlib import Path
from enum import Enum
from loguru import logger

from virtual_to_news.web_crawler.news import News
from virtual_to_news.trending import trending_keywords, google_trends
from virtual_to_news.git_command import GitCommand

cli = typer.Typer(help="Virtual to News -- 將AI帶入你的生活。")


class KeywordFunctions(str, Enum):
    segmentation = "segmentation"
    keyword = "keyword"
    trend = "trend"


mode_list = ["mode_a", "mode_b", "mode_c"]

keep_duplicated_keywords_only_desc = """
決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析，用以減少 api request 次數。
使用情境：
「True」，若輸入關鍵字為爬蟲後未處理的大量關鍵字(>100個)。
「False」，若輸入關鍵字為精確的少量關鍵字(<100個)。"""


tournament_desc = """(錦標賽) 回傳的最熱門關鍵字數量，
CHAMPION: 回傳1個關鍵字。
FINAL: 回傳進入決賽關鍵字，1~5個。
SEMI_FINAL: 回傳進入半決賽關鍵字，6~25個。
QUARTER_FINAL: 回傳進入四分之一決賽關鍵字，26~225個。
預設為 GoogleTrends.Tournament.FINAL"""


def tournament_checker(value: str):
    if value is None:
        return None

    if value.upper() in google_trends.GoogleTrends.Tournament.__members__:
        return value
    else:
        raise typer.BadParameter("Google Trends Tournament must be {CHAMPION|FINAL|SEMI_FINAL|QUARTER_FINAL}")


@cli.command()
def crawl(destination: Path = typer.Option(
              None,
              "--destination-path",
              "-d",
              help="自訂爬蟲結果輸出的路徑及檔名",
              show_default="assets/json/{year}/{month}/{day}/{website name}"),
          stop_day: int = typer.Option(
              7,
              "--stop-day",
              help="爬到幾天前要停止"),
          skip_repetitive: bool = typer.Option(
              True,
              "--skip-repetitive",
              help="決定是否要跳過重複爬取過的新聞"),
          multithread: bool = typer.Option(
              True,
              "--multithread/--multiprocess",
              "-m/-M",
              help="是：使用多執行緒爬蟲。否：使用多線程爬蟲。"),
          push_to_github: bool = typer.Option(
              False,
              "--push-to-github",
              help="自動推上 GitHub")):
    """
    執行網頁爬蟲。預設為每日bot上的爬蟲
    """
    logger.info("Starting crawl")

    if push_to_github:
        g = GitCommand()

    if destination is None:
        news = News()
        logger.trace("Destination is None")
    elif destination.is_dir():
        logger.trace(f"Folder path is :{destination}")
        news = News(folder_path=str(destination))
    else:
        logger.error("Destination_path must be a directory.")
        raise typer.BadParameter("Destination_path must be a directory.")

    if multithread:
        news.threading_get_news(skip_repetitive=skip_repetitive, stop_day=stop_day)
    else:
        news.process_get_news(skip_repetitive=skip_repetitive, stop_day=stop_day)

    if push_to_github:
        g.add_and_commit_and_push()

    typer.echo("web_crawler()")


@cli.command()
def keywords(function: KeywordFunctions = typer.Argument(
                 ...,
                 help="選擇功能",
                 case_sensitive=False),
             source_path: Path = typer.Option(
                 None,
                 "--source-path",
                 help="自訂輸入路徑及檔名"),
             destination_path: Path = typer.Option(
                 None,
                 "--destination-path",
                 help="自訂輸出路徑及檔名"),
             keywords: List[str] = typer.Argument(
                 None,
                 help="設定關鍵字list"),
             read_date_in_json: bool = typer.Option(
                 False,
                 help="是否直接透過 json 檔案中的時間來設定 google trends 的時間範圍"),
             keep_duplicated_keywords_only: bool = typer.Option(
                 None,
                 help=keep_duplicated_keywords_only_desc),
             tournament: str = typer.Option(
                 None,
                 callback=tournament_checker,
                 help=tournament_desc),
             category: int = typer.Option(
                 0,
                 help="Google Trends 的關鍵字類型。"),
             timeframe: str = typer.Option(
                 None,
                 help="用以手動調整 api 抓取數值的時間區間與間隔。")
             ):
    """
    關鍵字管理程式。包含切詞、關鍵字提取、google trends
    """

    if function is KeywordFunctions.segmentation:
        typer.echo("segment")

    if function is KeywordFunctions.keyword:
        typer.echo("keyword")

    if function is KeywordFunctions.trend:
        typer.echo("trend")

        if tournament is not None:
            _tournament = google_trends.GoogleTrends.Tournament[tournament]
        else:
            raise typer.BadParameter("Google Trends Tournament must be {CHAMPION|FINAL|SEMI_FINAL|QUARTER_FINAL}")

        if source_path is None and not keywords:
            raise typer.BadParameter("Source must be specified.")

        trkw = trending_keywords.TrendingKeyword(json_path=source_path,
                                                 keywords=list(keywords),
                                                 read_date_in_json=read_date_in_json)

        kw = trkw.get_trending_keyword(keep_duplicated_keywords_only=keep_duplicated_keywords_only,
                                       tournament=_tournament,
                                       category=category,
                                       timeframe=timeframe)
        typer.echo(f"trending_keywords is {kw}")


@cli.command()
def news():
    """
    新聞管理程式。包含「利用關鍵字找出現有資料庫中的相關新聞」。
    """
    pass


@cli.command()
def reporting_script():
    """
    主播講稿管理程式。透過給予的輸入資料生成講稿。
    """
    pass


if __name__ == "__main__":
    # 移除內建預設 logger
    logger.remove()

    # 加入寫檔logger
    logger.add("log/virtual_to_news.log", rotation="100 KB", level="TRACE", backtrace=True, diagnose=True)

    # 加入顯示在 terminal 的自定義 logger
    logger.add(sys.stdout, level="TRACE", backtrace=True, diagnose=True)
    cli()
