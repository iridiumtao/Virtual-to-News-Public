from os import listdir
from os.path import isdir, isfile, join

from news.common.handle_time import TakeTime


class FolderFile():
    def __init__(self,
                 source_path: str = './assets/json',
                 end_date: str = TakeTime.now_datetime(),
                 date_duration: int = 0):
        folder_list = []
        file_list = []
        file_path_list = []
        for i in range(0, date_duration+1):
            # 取日期資料夾
            end_year, end_month, end_day = TakeTime.take_need_day(end_date, i)
            folder = source_path+"/"+end_year + "/"+end_month+"/"+end_day

            if isdir(folder):
                # 資料夾各個檔案
                file_name = []
                for file_info in listdir(folder):
                    file_name.append(file_info)
                    file_path = join(folder, file_info)
                    file_path_list.append(file_path)
                file_list.append(file_name)
                folder_list.append(folder)
        self.folder_list = folder_list
        self.file_list = file_list
        self.file_path_list = file_path_list

    def get_folder_list(self):
        return self.folder_list

    def get_file_list(self):
        return self.file_list

    def get_folder_file_list(self):
        return self.folder_list, self.file_list

    def get_file_path_list(self):
        return self.file_path_list


if __name__ == "__main__":
    ff = FolderFile(end_date='2022-06-22', date_duration=2)
    print(ff.get_folder_list())
    print(ff.get_file_list())
    print(ff.get_folder_file_list())
    print(ff.get_file_path_list())
