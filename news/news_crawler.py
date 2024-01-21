import sys
from pathlib import Path

import typer
from loguru import logger

from news.git_command import GitCommand
from news.web_crawler.news import News

cli = typer.Typer(help="Virtual to News -- 將AI帶入你的生活。")


@cli.command()
def crawl(destination: Path = typer.Option(
    None,
    "--destination-path",
    "-d",
    help="自訂爬蟲結果輸出的路徑及檔名",
    show_default="./assets/json/{year}/{month}/{day}/{website name}"),
          date_duration: int = typer.Option(7,
                                            "--date-duration",
                                            "-n",
                                            help="爬到幾天前要停止。"),
          skip_repetitive: bool = typer.Option(
              True,
              "--skip-repetitive/--no-skip-repetitive",
              "-s/-S",
              help="決定是否要跳過重複爬取過的新聞。"),
          multithread: bool = typer.Option(True,
                                           "--multithread/--multiprocess",
                                           "-m/-M",
                                           help="選擇「多執行緒」爬蟲或「多線程」爬蟲。"),
          push_to_github: bool = typer.Option(
              False, "--push-to-github",
              help="自動推上 GitHub。（主機Git須具有repo的權限）")):
    """
    執行網頁爬蟲，自動將新聞以json格式儲存。爬蟲Bot藉由執行此指令每日爬蟲。

    預設將新聞儲存於 ./assets/json/{year}/{month}/{day}/{website name}。

    網站列表：鉅亨 Anue、科技新報 technews、中時新聞 chinatimes、聯合新聞網 udn、自由時報 ltn、今日新聞 nownews、旺得富 wantrich
    """
    logger.info("Starting crawl")

    if push_to_github:
        g = GitCommand(branch_name='news_crawler')

    if destination is None:
        news = News()
        logger.info("Destination is None, using default")
    elif destination.is_dir():
        logger.info(f"Folder path is :{destination}")
        news = News(folder_path=str(destination))
    else:
        logger.error("Destination_path must be a directory.")
        raise typer.BadParameter("Destination_path must be a directory.")

    if multithread:
        news.threading_get_news(skip_repetitive=skip_repetitive,
                                stop_day=date_duration)
    else:
        news.process_get_news(skip_repetitive=skip_repetitive,
                              stop_day=date_duration)

    if push_to_github:
        g.add_and_commit_and_push()

    logger.info("web_crawler finish")


if __name__ == "__main__":
    # 移除內建預設 logger
    logger.remove()

    # 加入寫檔logger
    logger.add("/news/log/news.log",
               rotation="100 KB",
               level="TRACE",
               backtrace=True,
               diagnose=True)

    # 加入顯示在 terminal 的自定義 logger
    logger.add(sys.stdout, level="TRACE", backtrace=True, diagnose=True)
    cli()
