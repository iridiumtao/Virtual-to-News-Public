# file version 0.1.6

# 必須確保各個 host name 及其 ports
# 與 Virtual-to-News/docker-compose.py 中的 service name 及 port 或 expose 完全一致
import json

virtual_to_news_host = "virtual-to-news"
virtual_to_news_port = "25501"
virtual_to_news_server_url = f"http://{virtual_to_news_host}:{virtual_to_news_port}/"

file_host = "file-server"
file_port = "25500"
file_server_url = f"http://{file_host}:{file_port}/"

news_host = "news-server"
news_port = "25505"
news_server_url = f"http://{news_host}:{news_port}/"

voice_host = "voice-server"
voice_port = "25504"
voice_server_url = f"http://{voice_host}:{voice_port}/"

lip_host = "lip-server"
lip_port = "25503"
lip_server_url = f"http://{lip_host}:{lip_port}/"

vtuber_host = "vtuber-server"
vtuber_port = "25502"
vtuber_server_url = f"http://{vtuber_host}:{vtuber_port}/"

is_debug_mode = True


class Parameters(object):

    def __init__(self,
                 status=None,
                 uuid=None,
                 transcript=None,
                 keyword_method=None,
                 source_path=None,
                 destination_path=None,
                 has_title=None,
                 end_date=None,
                 date_duration=None,
                 skip_repetitive=None,
                 category=None,
                 n_chars=None,
                 n_times_in_articles=None,
                 topic=None,
                 n_sentences=None,
                 shift_pitch=None,
                 voice_mode=None,
                 voice_wav_name=None):
        self.status = status
        self.uuid = uuid
        self.transcript = transcript
        self.keyword_method = keyword_method
        self.source_path = source_path
        self.destination_path = destination_path
        self.has_title = has_title
        self.end_date = end_date
        self.date_duration = date_duration
        self.skip_repetitive = skip_repetitive
        self.category = category
        self.n_chars = n_chars
        self.n_times_in_articles = n_times_in_articles
        self.topic = topic
        self.n_sentences = n_sentences
        self.shift_pitch = shift_pitch
        self.voice_mode = voice_mode
        self.voice_wav_name = voice_wav_name

    def __repr__(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, indent=4)

    def __str__(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, indent=4)
