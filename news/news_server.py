import json
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, request
from main import KeywordMethod, generate_news, get_transcript

from define import Parameters, is_debug_mode, news_host, news_port

app = Flask(__name__)

true_strings = ['true', '1', 't', 'y', 'yes', 'ture']

transcript_filename = "transcript.txt"
news_filename = "news.txt"


@app.route('/', methods=['POST'])
@app.route('/news', methods=['POST'])
def request_news():
    params_raw = request.values.get('data')
    status = request.values.get('status')

    app.logger.debug(params_raw)

    if status != "ok":
        app.logger.critical("status is not ok")
        return params_raw

    params = Parameters(**json.loads(params_raw))

    generate_news_defaults = generate_news.__defaults__

    if params.source_path is None:
        arg = generate_news_defaults[2]
        params.source_path = arg.default

    if params.destination_path is None:
        arg = generate_news_defaults[3]
        params.destination_path = arg.default

    if isinstance(params.has_title, str):
        params.has_title = params.has_title.lower() in true_strings
    if params.has_title is None:
        arg = generate_news_defaults[4]
        params.has_title = arg.default

    if params.end_date is None:
        arg = generate_news_defaults[5]
        params.end_date = arg.default

    if isinstance(params.date_duration, str):
        params.date_duration = int(params.date_duration)
    if params.date_duration is None:
        arg = generate_news_defaults[6]
        params.date_duration = arg.default

    if isinstance(params.skip_repetitive, str):
        params.skip_repetitive = params.skip_repetitive.lower() in true_strings
    if params.skip_repetitive is None:
        arg = generate_news_defaults[7]
        params.skip_repetitive = arg.default

    if isinstance(params.category, str):
        params.category = int(params.category)
    if params.category is None:
        arg = generate_news_defaults[8]
        params.category = arg.default

    if isinstance(params.n_sentences, str):
        params.n_sentences = int(params.n_sentences)
    if params.n_sentences is None:
        arg = generate_news_defaults[9]
        params.n_sentences = arg.default

    transcript_defaults = get_transcript.__defaults__

    uuid = params.uuid

    # 如果資料夾不存在則創資料夾
    output_dir = Path(f"./outputs/{uuid}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 如果檔案存在就不生成
    if (output_dir / transcript_filename).is_file():
        app.logger.info(f"{uuid}/{transcript_filename} 已經存在。跳過講稿生成。")
        # 讀取檔案中的新聞
        with open(output_dir / transcript_filename, 'r') as file:
            params.transcript = file.read()
    elif (output_dir / news_filename).is_file():
        app.logger.info(f"{uuid}/{news_filename} 已經存在。跳過文章生成。")
        # 讀取檔案中的新聞
        with open(output_dir / news_filename, 'r') as file:
            news = file.read()
        params.transcript = get_transcript(article=news,
                                           num=transcript_defaults[1].default,
                                           filename=transcript_filename,
                                           destination_path=str(output_dir))
    elif params.transcript is not None:
        app.logger.info("params.transcript 已經存在文章。跳過文章生成。")

        f = open(output_dir / transcript_filename, "w")
        f.write(params.transcript + "\n")
        f.close()
    else:
        news = generate_news(
            function=KeywordMethod[params.keyword_method],
            topic=params.topic,
            source_path=params.source_path,
            destination_path=str(output_dir),
            has_title=params.has_title,
            end_date=params.end_date,
            date_duration=params.date_duration,
            skip_repetitive=params.skip_repetitive,
            category=params.category,
            n_sentences=params.n_sentences,
            filename=news_filename
        )
        params.transcript = get_transcript(article=news,
                                           num=transcript_defaults[1].default,
                                           filename=transcript_filename,
                                           destination_path=str(output_dir))

    data = json.dumps(params, ensure_ascii=False, default=lambda o: o.__dict__)

    return data


@app.route('/topic', methods=['POST'])
def request_topic():
    date = request.values.get('date')
    if date is None:
        date = datetime.now()
    date_interval = request.values.get('date_interval')

    if date_interval is None:
        date_interval = 7

    topic = request.values.get('topic')
    if topic is not None:
        return topic

    if topic is None:
        # todo get topic
        return "popular_topic_here"


if __name__ == "__main__":
    app.run(debug=is_debug_mode, host=news_host, port=news_port)
