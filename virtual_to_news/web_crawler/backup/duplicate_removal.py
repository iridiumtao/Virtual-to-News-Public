import os
import pandas as pd
import time
# from handle_time import TakeTime
from pathlib import Path


file_path = "assets/json"
file_name = "duplicate_removal.json"
save_file_name ="no_repetition.json"
file = file_path+"/"+file_name

start_time = time.time()  # 開始時間
if os.path.isfile(file):
    df = pd.read_json(file)
    df = df.transpose()  # 轉換，為了符合儲存的樣子
else:
    print("file is not found")
    df=pd.DataFrame

print(df.shape)
df.drop_duplicates("content", keep="first", inplace=True)
print(df.shape)

end_time = time.time()
print(f"{end_time - start_time} ")


path = Path(file_path)
path.mkdir(parents=True, exist_ok=True)

name = path/save_file_name
df.to_json(name, orient='index', force_ascii=False, indent=4)
