from get_page import Dataset_df
from get_page import GetPage

from pathlib import Path

import threading
# import multiprocessing as mp

import time


def main():
    start_time = time.time()  # 開始時間
    file_path = "assets/json"
    file_name = "test0521.json"
    file = file_path+"/"+file_name

    lock = threading.Lock()
    dataset = Dataset_df(file, lock, 0)

    # 爬網頁  7
    x = 7
    threads = []
    for i in range(x):
        t = GetPage(dataset, i)
        threads.append(t)
        threads[i].start()

    for i in range(x):
        threads[i].join()


    df = dataset.return_df()

    # 寫檔-----------------------------------------------------------------------------------
    path = Path("./assets/json")
    path.mkdir(parents=True, exist_ok=True)
    name = path / file_name
    df.to_json(name, orient='index', force_ascii=False, indent=4)

    end_time = time.time()
    print(f"{end_time - start_time} ")
if __name__ == '__main__':
    main()
