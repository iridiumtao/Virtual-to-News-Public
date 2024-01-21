import json
from pathlib import Path

import requests
from flask import Flask, request
from voice_generator import voiceGenerator

from define import (Parameters, is_debug_mode, news_server_url, voice_host,
                    voice_port)

app = Flask(__name__)

fname = "voice.wav"


@app.route('/', methods=['POST'])
@app.route('/voice', methods=['POST'])
def request_voice():
    # 載入參數
    params_raw = request.values.get('data')

    status = request.values.get('status')
    if status != "ok":
        app.logger.critical("status is not ok")
        return params_raw

    # TODO: 加入判斷程式會不會正常執行的功能。比如檢查路徑是否存在

    app.logger.debug(params_raw)

    # 取得生成好的文章
    respond = requests.post(news_server_url, data={
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
    transcript = params.transcript

    if transcript is None:
        app.logger.critical("新聞沒有被生成。 Transcript was not generated.")
        return (r, 500)

    # 如果資料夾不存在則創資料夾
    output_dir = Path(f"./outputs/{uuid}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果檔案存在就不生成
    if (output_dir / fname).is_file():
        app.logger.info(f"{uuid}/{fname} 已經存在。跳過語音生成。")
        return r

    # 生成聲音
    voice = voiceGenerator()

    if params.voice_mode is not None:
        mode = params.voice_mode
    else:
        mode = voice.generate.__defaults__[6]

    if params.shift_pitch is not None:
        shift_pitch = params.shift_pitch
    else:
        shift_pitch = voice.generate.__defaults__[8]

    if params.voice_wav_name is not None:
        wav_name = params.voice_wav_name
    else:
        wav_name = voice.generate.__defaults__[2]

    voice.generate(wav_name=wav_name,
                   text=transcript,
                   output_dir=output_dir,
                   output_name=Path(fname).stem,
                   mode=mode,
                   shift_pitch=shift_pitch)

    # 將先前 request 回傳的參數回傳
    return r


if __name__ == "__main__":
    app.run(debug=is_debug_mode, host=voice_host, port=voice_port)
