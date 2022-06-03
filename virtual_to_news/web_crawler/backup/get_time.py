import os
import pandas as pd
import time
from handle_time import TakeTime
from pathlib import Path


file_path = "assets/json"
file_name = "duplicate_removal.json"
save_file_name ="overtime_removal.json"

file = file_path+"/"+file_name

start_time = time.time()  # 開始時間
if os.path.isfile(file):
    df = pd.read_json(file)
    df = df.transpose()  # 轉換，為了符合儲存的樣子
else:
    print("file is not found")
end_time = time.time()
print(f"{end_time - start_time} ")



new_df=df[(df['date']<TakeTime.take_now()) & (df['date']>TakeTime.take_head_day(7))]
# new_df = df[(df['date'] > TakeTime.take_head_day(7))]

print(new_df.shape[0])

path = Path(file_path)
path.mkdir(parents=True, exist_ok=True)
# file_name = TakeTime.take_file_day(TakeTime.take_now())+".json"
name = path/save_file_name
new_df.to_json(name, orient='index', force_ascii=False, indent=4)
