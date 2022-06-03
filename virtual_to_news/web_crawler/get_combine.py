from os import listdir
from os.path import isfile, isdir, join
import pandas as pd
from .handle_time import TakeTime


class GetCombine:
    """
    合併時間段內的資料
    """

    def __init__(self,
                 folder_path: str = './assets/json',
                 star_date: str = None,
                 day_ago: int = 7,
                 ):
        """
        合併時間段內的資料
        資料的路徑，最後時間，需要幾天

        :param folder_path: 路徑
        :type folder_path: str
        :param star_date: 日期(2022-06-01)(預設 today)
        :type star_date: str
        :param day_ago: 幾天前(預設 7)
        :type day_ago: int
        """
        if not star_date:
            star_date = TakeTime.now_datetime()[:10]
        self.folder_path = folder_path
        self.star_date = star_date
        self.day_ago = day_ago

    def all_folder(self):
        """
        查看全部的資料夾
        目前無作用
        """
        folder = self.folder_path
        files = listdir(folder)
        self.year_list = []
        self.month_lis = []
        for f in files:
            # 產生檔案的絕對路徑
            fullpath = join(folder, f)
            # 判斷 fullpath 是不是目錄
            if isdir(fullpath):
                if f != "keyword":
                    self.year_list.append(f)
                    files = listdir(folder+"/"+f)
                    self.month_lis.append(files)

    def run(self):
        """
        執行合併
        """

        df = pd.DataFrame(
            columns=["source", "title", "link", "date",
                     "keywords", "content", "summary"]
        )  # 定義空資料框，準備合併

        # 設定的時間往前合併檔案
        for i in range(0, self.day_ago):
            # 要合併的那天
            end_year, end_month, end_day = TakeTime.take_need_day(
                self.star_date, i)
            file = self.folder_path+"/"+end_year + \
                "/"+end_month+"/"+end_day
            # 看裡面有甚麼檔案去合併
            for file_info in listdir(file):
                file_path = join(file, file_info)
                new_df = pd.read_json(file_path).transpose()
                df = pd.concat([new_df, df], ignore_index=True)

        ori=df.shape[0] # 重複移除前
        df.drop_duplicates("content", keep="first", inplace=True)  # 去除內容重複的檔案
        after=df.shape[0] # 重複移除前
        print(f"{ori-after} removed")
        print(f"{after} remaining")

        name = end_year+"-"+end_month+"-"+end_day + \
            "--"+self.star_date+".json"
        file = self.folder_path+"/"+name
        df.reset_index(drop=True, inplace=True)  # 序號刷新，無排列
        df.to_json(file, orient='index', force_ascii=False, indent=4)  # 儲存檔案
