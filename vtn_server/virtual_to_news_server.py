import json
import time
import uuid
from pathlib import Path

import requests
from flask import Flask, request

from define import (Parameters, is_debug_mode, lip_server_url, news_server_url,
                    virtual_to_news_host, virtual_to_news_port,
                    voice_server_url, vtuber_server_url)

app = Flask(__name__)


@app.route('/')
def home():
    """
    首頁？

    但其實這隻程式是API的頭，如果要有網頁的話，應該要寫在別的地方

    """
    return 'Flask Dockerized by server A'


@app.route('/news', methods=['POST'])
def news():
    """
    請求新聞文稿

    以下 parameters 意指POST請求的輸入參數

    Parameters:
    ----------
    :param date: 文章搜尋日期，須符合ISO 8601

    :return: 新聞文稿
    :rtype: str
    """
    params = Parameters()
    receive_query_params(params)

    data = json.dumps(params, default=lambda o: o.__dict__)

    respond = requests.post(url=news_server_url, data={
        "data": data,
        "status": "ok"
    })
    if respond.status_code != 200:
        app.logger.error(f"news server response code: {respond.status_code}")
        app.logger.error(f"content: {respond.text}")
        return (respond.text, 500)

    r = respond.json()

    # 讀取成 object
    respond_params = Parameters(**r)

    write_params_to_file(params)

    return respond_params.transcript


@app.route("/vtuber", methods=['POST'])
@app.route("/video", methods=['POST'])
def vtuber():
    params = Parameters()
    receive_query_params(params)

    data = json.dumps(params, default=lambda o: o.__dict__)

    respond = requests.post(url=vtuber_server_url, data={
        "data": data,
        "status": "ok"
    })
    if respond.status_code != 200:
        app.logger.error(f"vtuber server response code: {respond.status_code}")
        return (respond.text, 500)

    r = respond.json()

    # 讀取成 object
    respond_params = Parameters(**r)

    write_params_to_file(params)

    return respond_params.uuid


@app.route("/voice", methods=['POST'])
def voice():
    params = Parameters()
    receive_query_params(params)

    data = json.dumps(params, default=lambda o: o.__dict__)

    respond = requests.post(url=voice_server_url, data={
        "data": data,
        "status": "ok"
    })
    if respond.status_code != 200:
        app.logger.error(f"voice server response code: {respond.status_code}")
        app.logger.error(f"content: {respond.text}")
        return (respond.text, 500)

    r = respond.json()

    # 讀取成 object
    respond_params = Parameters(**r)

    write_params_to_file(params)

    return respond_params.uuid


@app.route("/lip", methods=['POST'])
def lip():
    params = Parameters()
    receive_query_params(params)

    data = json.dumps(params, default=lambda o: o.__dict__)

    respond = requests.post(url=lip_server_url, data={
        "data": data,
        "status": "ok"
    })
    if respond.status_code != 200:
        app.logger.error(f"voice server response code: {respond.status_code}")
        return (respond.text, 500)

    r = respond.json()

    # 讀取成 object
    respond_params = Parameters(**r)

    write_params_to_file(params)

    return respond_params.uuid


def receive_query_params(params: Parameters):
    """讀取 Query Params 並存入 Parameters 中

    Parameters:
    ----------
    :param params: 存 query 參數的 object
    :type params: Parameters
    """
    params.transcript = request.values.get('transcript')
    params.keyword_method = request.values.get('keyword_method')
    params.source_path = request.values.get('source_path')
    params.destination_path = request.values.get('destination_path')
    params.has_title = request.values.get('has_title')
    params.end_date = request.values.get('end_date')
    params.date_duration = request.values.get('date_duration')
    params.skip_repetitive = request.values.get('skip_repetitive')
    params.category = request.values.get('category')
    params.topic = request.values.get('topic')
    params.uuid = request.values.get('uuid')
    params.n_sentences = request.values.get('n_sentences')
    params.voice_mode = request.values.get('voice_mode')
    params.shift_pitch = request.values.get('shift_pitch')
    params.voice_wav_name = request.values.get('voice_wav_name')

    # 如果沒有填入uuid則自動生成
    # 手動填入uuid可以作為指定輸出資料夾名稱的方法
    if params.uuid is None:
        params.uuid = str(uuid.uuid4())


def write_params_to_file(params: Parameters):

    # 如果資料夾不存在則創資料夾
    output_dir = Path(f"./outputs/{params.uuid}")
    output_dir.mkdir(parents=True, exist_ok=True)

    data = json.dumps(params, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)

    f = open(output_dir / "metadata.json", "w")
    f.write(data + "\n")
    f.close()


if __name__ == "__main__":
    print("version: 0.0.10")
    app.run(debug=is_debug_mode, host=virtual_to_news_host, port=virtual_to_news_port)
