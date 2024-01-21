import json
import subprocess
from pathlib import Path

import requests
from define import (Parameters, is_debug_mode, lip_host, lip_port,
                    voice_server_url)
from flask import Flask, request

app = Flask(__name__)

fname = "lip_inference.mp4"

@app.route('/', methods=['POST'])
@app.route('/lip', methods=['POST'])
def request_lip():
    # 載入參數
    params_raw = request.values.get('data')
    status = request.values.get('status')
    if status != "ok":
        app.logger.error("status is not ok")
        return {
            'status': status,
            "data": params_raw
        }

    # TODO: 加入判斷程式會不會正常執行的功能。比如檢查路徑是否存在

    app.logger.debug(params_raw)

    # 取得生成好的文章
    respond = requests.post(voice_server_url, data={
        "data": params_raw,
        "status": status
    })

    # 防止前面的錯誤導致後面一連傳 crash
    if respond.status_code != 200:
        return (respond.text, 500)

    r = respond.json()

    # 讀取成 object
    params = Parameters(**r)

    # params = Parameters(**json.loads(params_raw))

    app.logger.debug(params)
    if params is None:
        app.logger.critical("params is None")
        return r

    uuid = params.uuid

    app.logger.debug(uuid)

    # 如果資料夾不存在則創資料夾
    output_dir = Path(f"./outputs/{uuid}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果檔案存在就不生成
    if (output_dir / fname).is_file():
        app.logger.info(f"{uuid}/{fname} 已經存在。跳過嘴型生成。")
        return r

    cmd = [
        "python", "inference.py", "--checkpoint-path", "./checkpoints/wav2lip.pth", "--face",
        "./base_video", "--audio", f"./{str(output_dir)}/voice.wav", "--outfile",
        f"./{str(output_dir)}/{fname}"
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in p.stdout:
        app.logger.debug(line)
    p.wait()

    app.logger.info(f"Wav2lip inference return code: {p.returncode}")

    if p.returncode != 0:
        app.logger.error(f"Wav2lip inference return code is not 0")
        return (r, 500)

    # 將先前 request 回傳的參數回傳
    return r


if __name__ == "__main__":
    app.run(debug=is_debug_mode, host=lip_host, port=lip_port)
