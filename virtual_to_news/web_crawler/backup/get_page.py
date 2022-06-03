import os
import pandas as pd
import random
import time
import threading
# from multiprocessing import Process

import urllib.request as req
import json
import requests
from bs4 import BeautifulSoup

from agent import headers  # 不同使用者
from handle_time import TakeTime


class Dataset_df():
    def __init__(self, file, lock, all_test):
        """
        用於儲存爬完的文章資料。
        檔案路徑有則讀取(只能讀json)，再轉換成可以寫入的方式。
        檔案路徑無則新增空的dataframe。

        :param file: 原來資料路徑
        :type file: datafram
        :param lock: 多線程鎖
        :type lock: threading.lock
        :param all_test: 看到爬過的是否繼續往下爬，1繼續
        :type all_test: boolean
        """
        # 看檔案有無存在，有則讀，無則創造
        if os.path.isfile(file):
            df = pd.read_json(file)
            df = df.transpose()  # 轉換，為了符合儲存的樣子
        else:
            df = pd.DataFrame(
                columns=["source", "title", "link", "date",
                         "keywords", "content", "summary"]
            )  # 定義空資料框
        self.df = df
        self.lock = lock
        self.all_test = all_test

    def save_df(self, df):
        """
        儲存爬完的文章資料，
        若無爬過則儲存，
        有爬過看要不要結束

        :param df: 新爬到的文章
        :type df: datafram
        :param lock: 多線程鎖
        :type lock: threading.lock
        :param all_test: 看到爬過的是否繼續往下爬，1繼續
        :type all_test: boolean
        """
        # if df.shape[0]:
        #     self.lock.acquire()
        #     self.df = pd.concat([self.df, df], ignore_index=True)
        #     self.lock.release()
        if df["link"][0] not in self.df["link"].values and df.shape[0]:
            self.lock.acquire()
            self.df = pd.concat([self.df, df], ignore_index=True)
            self.lock.release()
        else:
            return self.all_test

    def return_df(self):
        """
        回傳爬完的東西

        return: 回傳全部文章
        rtype:dataframe
        """
        return self.df


class GetPage(threading.Thread):
    def __init__(self, dataset, num):
        """
        繼承多線程，多的網站可以一起爬。

        :param dataset: 原來資料
        :type dataset: datafram
        :param num: 幾個網站
        :type num: int
        """
        threading.Thread.__init__(self)
        self.num = num
        self.dataset = dataset

    def run(self):
        if self.num == 0:
            self.wan_get()
        elif self.num == 1:
            self.anue_get()
        elif self.num == 2:
            self.technew_get()
        elif self.num == 3:
            self.chinatimes_get()
        elif self.num == 4:
            self.udn_get()
        # elif self.num == 5:
        #     self.ltn_get()
        elif self.num == 6:
            self.nownews_get()

    def wan_get(self):
        """
        wantrich 旺得富
        無可用 來自中華時報 無法溯源
        需定期爬取累積資料 1頁15篇 總共10頁
        """

        wan_url = "https://wantrich.chinatimes.com/newslist/42/"
        pages = 10

        # 網站列抓取每頁
        for num in range(1, pages+1):
            print(wan_url+str(num))
            resp = requests.get(wan_url+str(num), headers=headers())
            soup = BeautifulSoup(resp.text, "lxml")
            elem = soup.select(".vertical-list li")

            # 頁中抓取，標題、連結、時間，內文使用連結繼續爬
            for e in elem:
                title = e.select_one("h3.title").text
                link = "https://wantrich.chinatimes.com" + \
                    str(e.select_one("h3 a")["href"])
                date = int(e.select_one("time")["datetime"])
                content = WanGetCotent(link)
                # print(link)
                wan_df = pd.DataFrame({
                    "source": ["wantrich"],
                    "title": [title],
                    "link": [link],
                    "date": [date],
                    "content": [content]
                })
                end = self.dataset.save_df(wan_df)
                if end == 0:
                    return 0

    def anue_get(self):
        """
        Anue 鉅亨 有api可以用
        """
        # api抓資料 使用：每頁幾個&limit=30、第幾頁&page=1、時間不能間隔不能超過一年、時間使用Unix時間戳
        # 只取newsid、title、summary：https://api.cnyes.com/media/api/v1/newslist/all?startAt=1467734400&endAt=1644681599&limit=30
        # 全部訊息 https://api.cnyes.com/media/api/v1/newslist/category/headline?startAt=1467734400&endAt=1468734400&limit=30
        # 時間 1325343600 1328021999 1467734400 1468734400 1546272000 1551369599 1641312000 1644681599
        # https://api.cnyes.com/media/api/v1/newslist/category/headline?startAt=1641312000&endAt=1644681599&limit=30
        limit = 30  # 30
        anue_url = "https://api.cnyes.com/media/api/v1/newslist/category/headline?limit=" + \
            str(limit)
        years_ago = 0
        days_ago = 7
        for year in range(years_ago):
            if year or years_ago:
                anue_url_set = anue_url + \
                    "&startAt=" + str(TakeTime.take_head_year(year)) + \
                    "&endAt=" + str(TakeTime.take_last_year(year))
            else:
                anue_url_set = anue_url + \
                    "&startAt=" + str(TakeTime.take_head_day(days_ago)) + \
                    "&endAt=" + str(TakeTime.take_now())
            with req.urlopen(anue_url_set) as req1:
                reqload = json.load(req1)
            page = reqload["items"]["last_page"]
            for i in range(1, page+1):
                time.sleep(random.randint(1, 2))
                anue_url_target = anue_url_set+"&page="+str(i)
                print(anue_url_target)
                with req.urlopen(anue_url_target) as req2:
                    reqload = json.load(req2)
                data = reqload["items"]["data"]
                for ddata in data:
                    title = ddata["title"]
                    link = "https://news.cnyes.com/news/id/" + \
                        str(ddata["newsId"])
                    date = ddata["publishAt"]
                    summary = ddata["summary"]
                    content_tmp = BeautifulSoup(ddata["content"], 'lxml')
                    content_list = BeautifulSoup(content_tmp.text, 'lxml')
                    content = ""
                    for c in content_list:
                        content += c.text+"\n"

                    aune_df = pd.DataFrame({
                        "source": ["Aune"],
                        "title": [title],
                        "link": [link],
                        "date": [date],
                        "content": [content],
                        "summary": [summary]
                    })
                    end = self.dataset.save_df(aune_df)
                    if end == 0:
                        return 0

    def technew_get(self):
        """
        technews 無可用
        """
        technew_url = "https://finance.technews.tw"
        resp = requests.get(technew_url, headers=headers())
        soup = BeautifulSoup(resp.text, "lxml")
        elem = soup.select_one("div.pagination span").text
        # pages = int(''.join([x for x in elem[2:len(elem)] if x.isdigit()]))
        pages = 10
        for num in range(1, pages+1):
            print(technew_url+"/page/"+str(num))
            resp = requests.get(technew_url+"/page/" +
                                str(num), headers=headers())
            soup = BeautifulSoup(resp.text, "lxml")
            elem = soup.select(
                "div#content article div.content header.entry-header")
            for e in elem:
                try:
                    title = e.select_one("h1 a").get("title")
                    link = e.select_one("h1 a").get("href")
                    date = e.select("tr td span.body")[1].text
                    content = technewGetCotent(link)
                    date = date.replace(" 年 ", "-")
                    date = date.replace(" 月 ", "-")
                    date = date.replace(" 日", "")
                    date = date.strip()+":00"
                    date = TakeTime.datetime_timestamp(date)

                    technew_df = pd.DataFrame({
                        "source": ["technew"],
                        "title": [title],
                        "link": [link],
                        "date": [date],
                        "content": [content]
                    })
                    end = self.dataset.save_df(technew_df)
                    if end == 0:
                        return 0
                except:
                    content = "error"
                    print(date)
                    print("error null")
                    continue

    def chinatimes_get(self):
        """
        chinatimes 中時新聞 同 旺得富
        """
        url = "https://www.chinatimes.com/money/total?page="
        pages = 10
        for num in range(1, pages+1):
            print(url+str(num))
            resp = requests.get(url+str(num), headers=headers())
            soup = BeautifulSoup(resp.text, "lxml")
            elem = soup.select(".vertical-list li")
            for e in elem:
                title = e.select_one("h3.title").text
                link = e.select_one("h3 a")["href"]
                date = e.select_one("time")["datetime"]
                link = "https://www.chinatimes.com"+str(link)
                content = ChinatimesGetCotent(link)
                date = date.strip()+":00"
                date = TakeTime.datetime_timestamp(date)

                chinatimes_df = pd.DataFrame({
                    "source": ["chinatimes"],
                    "title": [title],
                    "link": [link],
                    "date": [date],
                    "content": [content]
                })
                end = self.dataset.save_df(chinatimes_df)
                if end == 0:
                    return 0

    def udn_get(self):
        """
        ubn 聯合新聞網 有api可以用
        """
        # &type=subcate_articles&sub_id=121591&totalRecNo=21 個人理財
        # &type=subcate_articles&sub_id=7241&totalRecNo=177 產業綜合
        # &type=subcate_articles&sub_id=7243&totalRecNo=36 稅務法務
        # &type=subcate_articles&sub_id=7239&totalRecNo=112 金融要聞
        # &type=subcate_articles&sub_id=7240&totalRecNo=112 科技產業
        # &type=subcate_articles&sub_id=7238&totalRecNo=121 財經焦點
        # &type=cate_latest_news&cate_id=6644&totalRecNo=815 最新文章
        # https://udn.com/api/more?channelId=2&cate_id=6644&type=subcate_articles&page=82
        # https://udn.com
        udn_url = "https://udn.com/api/more?channelId=2&cate_id=6644&type=subcate_articles&page="
        pages = 10
        for num in range(1, pages+1):
            urlpage = udn_url+str(num)
            print(urlpage)
            with req.urlopen(urlpage) as req1:
                reqload = json.load(req1)
            page = reqload["lists"]
            for e in page:
                title = e["title"]
                link = e["titleLink"]
                date = e["time"]["date"]
                link = "https://udn.com"+str(link)
                date = date.strip()+":00"
                date = TakeTime.datetime_timestamp(date)
                content = udnGetCotent(link)

                if content != "error":
                    udn_df = pd.DataFrame({
                        "source": ["udn"],
                        "title": [title],
                        "link": [link],
                        "date": [date],
                        "content": [content]
                    })
                    end = self.dataset.save_df(udn_df)
                    if end == 0:
                        return 0

    def ltn_get(self):
        """
        ltn 自由時報
        12(page)*20(new)連續可能會被ban
        """

        category = ["international", "investment", "securities", "strategy"]
        # category = ["investment"]
        # pages = [1, 1, 1, 1]
        pages = [500, 122, 500, 500]
        # pages = [25, 25, 25, 25]
        ltn_url = "https://ec.ltn.com.tw/list_ajax/"
        for c in range(0, len(category)):
            urlcate = ltn_url+category[c]+"/"
            for num in range(1, pages[c]+1):
                urlpage = urlcate+str(num)
                print(urlpage)
                time.sleep(random.randint(2, 3))
                with req.urlopen(urlpage) as req1:
                    reqload = json.load(req1)
                for e in reqload:
                    title = e["LTNA_Title"]
                    link = e["url"]
                    date = e["A_ViewTime"]
                    content = ltnGetCotent(link)
                    date = date.replace("/", "-")
                    date = date.strip()+":00"
                    date = TakeTime.datetime_timestamp(date)

                    ltn_df = pd.DataFrame({
                        "source": ["ltn"],
                        "title": [title],
                        "link": [link],
                        "date": [date],
                        "content": [content]
                    })
                    end = self.dataset.save_df(ltn_df)
                    if end == 0:
                        return 0

    def nownews_get(self):
        """
        nownews 今天新聞 有api
        """
        # https://www.nownews.com/nn-client/api/v1/cat/finance/?pid=5489349
        # pid 取文章最後面
        # https://www.nownews.com/cat/finance/
        nownews_url = "https://www.nownews.com/cat/finance/"
        resp = requests.get(nownews_url, headers=headers())
        soup = BeautifulSoup(resp.text, "lxml")
        elem = soup.select_one("div.swiper-slide a")
        href = elem.get("href")
        id = href.replace('https://www.nownews.com/news/', '')
        id1 = ""
        page = 10
        while (id != id1 and page):
            page -= 1
            trgate = "https://www.nownews.com/nn-client/api/v1/cat/finance/?pid="+id
            id1 = id
            print(trgate)
            with req.urlopen(trgate) as req2:
                reqload = json.load(req2)
            data = reqload["data"]["newsList"]
            for ddata in data:
                title = ddata["postTitle"]
                link = "https://www.nownews.com"+str(ddata["postOnlyUrl"])
                date = ddata["newsDate"]
                content = nownewsGetContent(link)
                date = date.strip()+":00"
                date = TakeTime.datetime_timestamp(date)

                nownews_df = pd.DataFrame({
                    "source": ["nownew"],
                    "title": [title],
                    "link": [link],
                    "date": [date],
                    "content": [content],
                })
                end = self.dataset.save_df(nownews_df)
                if end == 0:
                    return 0
            id = ddata["id"]


def WanGetCotent(target_url):
    content = ""
    try:
        r = requests.get(target_url, headers=headers())
        web_content = r.text
        soup = BeautifulSoup(web_content, "lxml")

        contentlist = soup.find("div", itemprop="articleBody")
        elsecontent = contentlist.find("p", dir="ltr")  # 例外崁入twitter
        articleContent = contentlist.select("p")

        for p in articleContent:
            if p.text != "":
                if elsecontent == None or p.text != elsecontent.text:
                    content = content + p.text + "\n"
    except:
        content = "error"
        print("error null")
    return(content)


def AuneGetContent(page, AnueUrl, df):
    AnueUrlSet = AnueUrl+"&page="+str(page)
    with req.urlopen(AnueUrlSet) as req2:
        reqload = json.load(req2)
    data = reqload["items"]["data"]
    for ddata in data:
        title = ddata["title"]
        link = "https://news.cnyes.com/news/id/"+str(ddata["newsId"])
        date = ddata["publishAt"]
        content = ddata["content"]
        summary = ddata["summary"]
        tmp = BeautifulSoup(content, 'lxml')
        tmp = BeautifulSoup(tmp.text, 'lxml')
        content = ""
        for c in tmp:
            content += c.text+"\n"
        df2 = pd.DataFrame({
            "source": ["Aune"],
            "title": [title],
            "link": [link],
            "date": [date],
            "content": [content],
            "summary": [summary]
        })
        df = pd.concat([df, df2], ignore_index=True)
    return (df)


def technewGetCotent(target_url):
    content = ""
    try:
        r = requests.get(target_url, headers=headers())
        web_content = r.text
        soup = BeautifulSoup(web_content, "lxml")
        contentlist = soup.find("div", class_="indent")
        articleContent = contentlist.select("p")
        for p in articleContent:
            if p.text != "":
                content = content + p.text + "\n"
    except:
        content = "error"
        print("error null")
    return(content)


def ChinatimesGetCotent(target_url):
    content = ""
    try:
        r = requests.get(target_url, headers=headers())
        web_content = r.text
        soup = BeautifulSoup(web_content, "lxml")

        contentlist = soup.find("div", itemprop="articleBody")
        elsecontent = contentlist.find("p", dir="ltr")  # 例外崁入twitter
        articleContent = contentlist.select("p")

        for p in articleContent:
            if p.text != "":
                if elsecontent == None or p.text != elsecontent.text:
                    content = content + p.text + "\n"
    except:
        content = "error"
        print("error null")
    return(content)


def udnGetCotent(link):
    content = ""
    try:
        r = requests.get(link, headers=headers())
        web_content = r.text
        soup = BeautifulSoup(web_content, "lxml")
        contentlist = soup.find(
            "section", class_="article-content__editor")
        articleContent = contentlist.select("p")
        for p in articleContent:
            if p.text != "":
                content = content + p.text.strip() + "\n"
    except:
        content = "error"
        print("error null")
    return(content)


def ltnGetCotent(link):
    content = ""
    try:
        time.sleep(random.randint(1, 2))
        r = requests.get(link, headers=headers())
        web_content = r.text
        soup = BeautifulSoup(web_content, "lxml")
        contentlist = soup.find("div", class_="text")
        articleContent = contentlist.select("p")
        for p in articleContent[1:len(articleContent)-2]:
            if p.text != "" and p.text != "請繼續往下閱讀...":
                content = content + p.text + "\n"
    except:
        content = "error"
        print("error null")
    return(content)


def nownewsGetContent(link):
    content = ""
    r = requests.get(link, headers=headers())
    web_content = r.text
    soup = BeautifulSoup(web_content, "lxml")
    contentlist = soup.find("article")
    for c in contentlist('br')+contentlist('div'):
        c.extract()
    for p in contentlist:
        try:
            article = p.string.strip()
            if article != "popin純文字廣告" and article != "dable純文字廣告" and article != "":
                content += article + "\n"
        except:
            content = "error"
            print("error null")
    return(content)


# class test_p(Process):
#     def __init__(self, test_dataset, num):
#         Process.__init__(self)
#         self.num = num
#         self.test_dataset = test_dataset

#     def run(self):
#         if self.num == 0:
#             self.wan_get()
#         elif self.num == 1:
#             self.anue_get()
#         elif self.num == 2:
#             self.technew_get()
#         elif self.num == 3:
#             self.chinatimes_get()
#         elif self.num == 4:
#             self.udn_get()
#         elif self.num == 6:
#             self.nownews_get()
#         # if self.num == 5:
#         #     self.ltn_get()
