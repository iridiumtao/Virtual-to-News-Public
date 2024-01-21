from news.web_crawler.get_combine import GetCombine
from news.web_crawler.get_page_process import GetPageProcess
from news.web_crawler.get_page_threading import GetPageThreading


class News ():
    """
    新聞爬取與結合資料
    """

    def __init__(self,
                 folder_path: str = './assets/json'):
        """
        新聞爬取與結合資料

        :param folder_path: 路徑
        :type folder_path: str
        """
        self.folder_path = folder_path
        self.news_websites = ['wan',
                              'anue',
                              'technew',
                              'chinatimes',
                              'udn',
                              'ltn',
                              'nownews']

    def process_get_news(self,
                         skip_repetitive: bool = True,
                         stop_day: int = 7):
        """
        多進程新聞爬取，有7個網站。

        :param skip_repetitive: 爬過的文章要不要繼續爬 
        :type folder_path: bool
        True : 跳過重複的文章(遇到重複文章即停止爬蟲) 
        False: 不跳過重複的文章(直到爬到 stop_day 停止日才停止爬蟲)
        :param stop_day: 爬到幾天前要停止
        :type stop_day: int
        """
        process = []
        for i in range(len(self.news_websites)):
            p = GetPageProcess(name=self.news_websites[i],
                               folder_path=self.folder_path,
                               skip_repetitive=skip_repetitive,
                               stop_day=stop_day)
            process.append(p)
            process[i].start()

        for i in range(len(self.news_websites)):
            process[i].join()

    def threading_get_news(self,
                           skip_repetitive: bool = True,
                           stop_day: int = 7):
        """
        多執行續新聞爬取，有7個網站。

        :param skip_repetitive: 爬過的文章要不要繼續爬 
        :type folder_path: bool
        True : 跳過重複的文章(遇到重複文章即停止爬蟲) 
        False: 不跳過重複的文章(直到爬到 stop_day 停止日才停止爬蟲)
        :param stop_day: 爬到幾天前要停止
        :type stop_day: int
        """
        threads = []
        for i in range(len(self.news_websites)):
            t = GetPageThreading(name=self.news_websites[i],
                                 folder_path=self.folder_path,
                                 skip_repetitive=skip_repetitive,
                                 stop_day=stop_day)
            threads.append(t)
            threads[i].start()

        for i in range(len(self.news_websites)):
            threads[i].join()

    def get_combine(self,
                    star_date: str = None,
                    date_duration: int = 7):
        """
        合併時間段內的資料

        :param star_date: 日期(2022-06-01)(預設 today)
        :type star_date: str
        :param date_duration: 幾天前(預設 7)
        :type date_duration: int
        """
        combine = GetCombine(folder_path=self.folder_path,
                             star_date=star_date,
                             date_duration=date_duration,)
        combine.run()
        print(f"combine {date_duration} day finish")


if __name__ == '__main__':
    folder_path = './assets/json'
    news = News(folder_path)
    # 爬取部分
    # news.process_get_news(skip_repetitive=1,
    #                       stop_day=1)
    # news.process_get_news()
    news.threading_get_news()

    # 合併部分
    # news.get_combine()
    # news.get_combine(star_date='2022-06-01',
    #                  date_duration=2)
    # news.get_combine(date_duration=2)
