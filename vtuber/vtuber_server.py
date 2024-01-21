import subprocess
from pathlib import Path
from time import sleep

import requests
from adjust_duration import get_duration
from flask import Flask, request

from define import (Parameters, is_debug_mode, lip_server_url, vtuber_host,
                    vtuber_port)

app = Flask(__name__)

video_input_file_name = 'virtual_to_news_temp.mp4'
video_output_file_name = 'virtual_to_news.mp4'
video_temp_file_name = 'virtual_to_news_temp_ver2.mp4'
audio_file_name = 'voice.wav'
lip_file_name = 'lip_inference.mp4'
video_file_path = './unity_vtuber/Recordings'


def debug(cmd, name):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in p.stdout:
        app.logger.debug(line)
    p.wait()
    content = 'success' if not p.returncode else 'fail'
    # app.logger.info(f"{name} return code: {p.returncode}")
    app.logger.info(f"{name}: {content}")
    if p.returncode != 0:
        app.logger.critical(f"{name} return code is not 0")
        return 500
    return 200


@app.route("/", methods=['POST'])
@app.route("/vtuber", methods=['POST'])
def request_vtuber():
    # 載入參數
    params_raw = request.values.get('data')

    status = request.values.get('status')
    if status != "ok":
        app.logger.critical("status is not ok")
        return params_raw

    # TODO: 加入判斷程式會不會正常執行的功能。比如檢查路徑是否存在

    # 請求嘴型生成
    respond = requests.post(lip_server_url, data={
        "data": params_raw,
        "status": status
    })

    # 防止前面的錯誤導致後面一連傳 crash
    if respond.status_code != 200:
        return (respond.text, 500)

    r = respond.json()

    # 讀取成 object
    params = Parameters(**r)

    # 如果沒有傳入參數就 early return
    app.logger.debug(params)
    if params is None:
        app.logger.critical("params is None")
        return r

    uuid = params.uuid

    # 如果資料夾不存在則創資料夾
    output_dir_path = Path(f"./outputs/{uuid}")
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_dir_str = str(output_dir_path)

    # 執行main tcp連線
    if not Path(f"{output_dir_str}/{audio_file_name}").is_file():
        app.logger.critical("Audio not found before running main. Aborting.")
        return (r, 500)
    cmd = [
        "python", "main.py", "--connect", "--file-path", f"{output_dir_str}/{lip_file_name}",
        "--mode", "file", "--host", "host.docker.internal"
    ]
    error_number = debug(cmd, name='Vtuber')
    if error_number != 200:
        return (r, error_number)

    # 執行影片變速
    if not Path(f"{video_file_path}/{video_input_file_name}").is_file():
        app.logger.critical("Video not found before running adjust_duration. Aborting.")
        return (r, 500)
    if not Path(f"{output_dir_str}/{audio_file_name}").is_file():
        app.logger.critical("Audio not found before running adjust_duration. Aborting.")
        return (r, 500)
    # 執行影片變速
    # cmd = [
    #     "python", "adjust_duration.py",
    #     "--audio-file-path", f"{output_dir_str}/{audio_file_name}",
    #     "--video-input-file-path", f"{video_file_path}/{video_input_file_name}",
    #     "--video-output-file-path", f"{video_file_path}/{video_temp_file_name}"
    # ]

    # 提取需變速數據
    duration, duration2 = get_duration(output_dir_str + "/" + audio_file_name,
                                       video_file_path + "/" + video_input_file_name)
    app.logger.info(f"Original_duration{duration}")
    app.logger.info(f"Change_duration{duration2}")
    # 執行影片變速
    cmd = [
        "ffmpeg", "-i", f"{video_file_path}/{video_input_file_name}", "-vf",
        f"setpts=PTS/{duration}*{duration2}", "-r", "30",
        f"{video_file_path}/{video_temp_file_name}", "-y", "-loglevel", "warning"
    ]
    error_number = debug(cmd, name='Adjust_Duration')
    if error_number != 200:
        return (r, error_number)

    # ffmpeg合併影音檔
    if not Path(f"{video_file_path}/{video_temp_file_name}").is_file():
        app.logger.critical("Video not found before running FFmpeg. Aborting.")
        return (r, 500)
    cmd = [
        "ffmpeg", "-i", f"{video_file_path}/{video_temp_file_name}", "-i",
        f"{output_dir_str}/{audio_file_name}", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
        f"{output_dir_str}/{video_output_file_name}", "-y", "-loglevel", "warning"
    ]
    error_number = debug(cmd, name='Audio_Visual_Combination')
    if error_number != 200:
        return (r, error_number)

    return r


if __name__ == "__main__":
    app.run(debug=is_debug_mode, host=vtuber_host, port=vtuber_port)
