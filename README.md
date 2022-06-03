# Virtual-to-News

Virtual to News Backend management program.

提供網頁爬蟲、新聞資料庫管理、關鍵字熱度分析、新聞關鍵字提取。 

## Introduction
Cooperated with teammates and designed an AI operated Virtual YouTuber (still working on it).

Generate scripts from popular financial news utilizing web crawling, natural language processing.

## Features
- Web crawling
- News keywords extraction
- Trending keywords analysis
- News database management

## Installation
Python 3.8 or newer is required.

Clone this repository
```shell
git clone https://github.com/jerry960331/Virtual-to-News-Public.git
```

Auto installation:

(Minimum requirements) If you need only need to run web crawler.
```shell
pip install -r crawler_requirements.txt
```

(Completion requirements) If you want everything.
```shell
pip install -r requirements.txt
```
Full requirements:
- pandas~=1.4.1
- loguru~=0.6.0
- typer~=0.3.2
- requests~=2.26.0 (crawler)
- beautifulsoup4~=4.10.0 (crawler)
- jieba~=0.42.1 (crawler, optional, deprecated)
- ckipnlp~=1.0.2 (crawler, optional, deprecated)
- numpy~=1.22.3 (keywords)
- tqdm~=4.64.0 (keywords)
- networkx~=2.7.1 (keywords)
- pytrends~=4.8.0 (trending)

## Usages
### Main
```shell
$ python main.py --help                                                                                                   
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Virtual to News -- 將AI帶入你的生活。

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  crawl             執行網頁爬蟲。預設為每日bot上的爬蟲
  keywords          關鍵字管理程式。包含切詞、關鍵字提取、google trends
  news              新聞管理程式。包含「利用關鍵字找出現有資料庫中的相關新聞」。
  reporting-script  主播講稿管理程式。透過給予的輸入資料生成講稿。

```

### Web crawler
```shell
$ python main.py crawl --help                                                                                                
Usage: main.py crawl [OPTIONS]

  執行網頁爬蟲。預設為每日bot上的爬蟲

Options:
  -d, --destination-path PATH     自訂爬蟲結果輸出的路徑及檔名  [default:
                                  (assets/json/{year}/{month}/{day}/{website
                                  name})]
  --stop-day INTEGER              爬到幾天前要停止  [default: 7]
  --skip-repetitive               決定是否要跳過重複爬取過的新聞  [default: True]
  -m, --multithread / -M, --multiprocess
                                  是：使用多執行緒爬蟲。否：使用多線程爬蟲。  [default:
                                  multithread]
  --push-to-github                自動推上 GitHub
  --help                          Show this message and exit.

```

### keywords
```shell
$ python main.py keywords --help
Usage: main.py keywords [OPTIONS] FUNCTION:{segmentation|keyword|trend}
                        [KEYWORDS]...

  關鍵字管理程式。包含切詞、關鍵字提取、google trends

Arguments:
  FUNCTION:{segmentation|keyword|trend}
                                  選擇功能  [required]
  [KEYWORDS]...                   設定關鍵字list

Options:
  --source-path PATH              自訂輸入路徑及檔名
  --destination-path PATH         自訂輸出路徑及檔名
  --read-date-in-json / --no-read-date-in-json
                                  是否直接透過 json 檔案中的時間來設定 google trends 的時間範圍
                                  [default: no-read-date-in-json]
  --keep-duplicated-keywords-only / --no-keep-duplicated-keywords-only
                                  決定是否只將出現一次以上的關鍵字進行流行趨勢(trends)分析，用以減少 api
                                  request 次數。 使用情境：
                                  「True」，若輸入關鍵字為爬蟲後未處理的大量關鍵字(>100個)。
                                  「False」，若輸入關鍵字為精確的少量關鍵字(<100個)。
  --tournament TEXT               (錦標賽) 回傳的最熱門關鍵字數量， CHAMPION: 回傳1個關鍵字。 FINAL:
                                  回傳進入決賽關鍵字，1~5個。 SEMI_FINAL:
                                  回傳進入半決賽關鍵字，6~25個。 QUARTER_FINAL:
                                  回傳進入四分之一決賽關鍵字，26~225個。 預設為
                                  GoogleTrends.Tournament.FINAL
  --category INTEGER              Google Trends 的關鍵字類型。  [default: 0]
  --timeframe TEXT                用以手動調整 api 抓取數值的時間區間與間隔。
  --help                          Show this message and exit.
```

## Structure 專案結構說明
```
├── docs
│   ├── docs.txt
│   └── VirtualToNews NLP小組 流程圖 20220407.drawio
├── LICENSE 授權條款，由 GitHub 生成
├── main.py 整隻程式的執行入口，可直接用指令界面執行
├── README.md 本說明文件
├── references 參考程式碼、以前寫的code
├── requirements.txt 本專案所使用的套件
├── scripts 測試用及雜項程式檔案
└── virtual_to_news 相當於 /src 資料夾，放置專案所需的程式檔
    ├── article_analyzer.py 
    ├── database_keyword_analyzer.py
    ├── git_command.py Git自動推送控制
    ├── keywords 關鍵字處理
    ├── test 測試檔案
    ├── trending 趨勢關鍵字
    └── web_crawler 網路爬蟲
```