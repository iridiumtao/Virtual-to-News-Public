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

### Clone this repository
```shell
git clone https://github.com/jerry960331/Virtual-to-News-Public.git
```

### Minimum requirements
If you need only need to run web crawler.

Run
```shell
pip install -r crawler_requirements.txt
```

###　Completion requirements
If you want everything.

Install PyTorch for your CUDA or ROCm version first.

Then, run
```shell
pip install -r requirements.txt
```
Full requirements:
 - pandas>=1.4.2
 - networkx~=2.6.3 #2.7.0 is not work
 - ckip-transformers~=0.3.2
 - loguru>=0.6.0
 - opencc-python-reimplemented~=0.1.6
 - pytrends>=4.8.0
 - scipy~=1.7.3
 - spacy~=3.3.1
 - beautifulsoup4~=4.10.0
 - GitPython~=3.1.29
 - Flask~=2.2.2
 - requests~=2.28.1
 - typer~=0.7.0
 - jieba~=0.42.1
 - tqdm>=4.27

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
  crawl          執行網頁爬蟲，自動將新聞以json格式儲存。爬蟲Bot藉由執行此指令每日爬蟲。
  extract        文章提取。
  generate-news  新聞處理的pipeline。一鍵執行提取關鍵字、流行關鍵字、文章提取。
  keywords       關鍵詞提取。
  trend          關鍵字流行比較，使用 Google Trends。

```

### Generate News
```shell
$ python main.py generate-news --help
Usage: main.py generate-news [OPTIONS]
                             FUNCTION:{keyword|keyword_jieba|noun_ner}

  新聞處理的pipeline。一鍵執行提取關鍵字、流行關鍵字、文章提取。

Arguments:
  FUNCTION:{keyword|keyword_jieba|noun_ner}
                                  選擇功能  [required]

Options:
  -s, --source-path TEXT          自訂輸入路徑  [default: ./assets/json]
  -d, --destination-asset-path TEXT
                                  自訂輸出路徑  [default: ./assets]
  --has-title / --no-title        是否把標題加入計算關鍵詞  [default: has-title]
  -e, --end-date TEXT             取的最後時間
  -n, --date-duration INTEGER     最後時間要往前取幾天  [default: 7]
  --skip-repetitive / --no-skip-repetitive
                                  是否要跳過重複類型的取關鍵字  [default: skip-repetitive]
  --category INTEGER              Google Trends 的關鍵字類型。  [default: 7]
  --help                          Show this message and exit.
```

### Web Crawl
```shell
$ python main.py crawl --help
Usage: main.py crawl [OPTIONS]

  執行網頁爬蟲，自動將新聞以json格式儲存。爬蟲Bot藉由執行此指令每日爬蟲。

  預設將新聞儲存於 ./assets/json/{year}/{month}/{day}/{website name}。

  網站列表：鉅亨 Anue、科技新報 technews、中時新聞 chinatimes、聯合新聞網 udn、自由時報 ltn、今日新聞
  nownews、旺得富 wantrich

Options:
  -d, --destination-path PATH     自訂爬蟲結果輸出的路徑及檔名  [default:
                                  (./assets/json/{year}/{month}/{day}/{website
                                  name})]
  -n, --date-duration INTEGER     爬到幾天前要停止。  [default: 7]
  -s, --skip-repetitive / -S, --no-skip-repetitive
                                  決定是否要跳過重複爬取過的新聞。  [default: skip-repetitive]
  -m, --multithread / -M, --multiprocess
                                  選擇「多執行緒」爬蟲或「多線程」爬蟲。  [default: multithread]
  --push-to-github                自動推上 GitHub。（主機Git須具有repo的權限）
  --help                          Show this message and exit.
```

### keywords
```shell
$ python main.py keywords --help
Usage: main.py keywords [OPTIONS] FUNCTION:{keyword|keyword_jieba|noun_ner}

  關鍵詞提取。

Arguments:
  FUNCTION:{keyword|keyword_jieba|noun_ner}
                                  選擇功能  [required]

Options:
  -s, --source-path TEXT          自訂輸入路徑  [default: ./assets/json]
  -d, --destination-path TEXT     自訂輸出路徑  [default: ./assets/json]
  --has-title / --no-title        是否把標題加入計算關鍵詞  [default: has-title]
  -e, --end-date TEXT             取的最後時間
  -n, --date-duration INTEGER     最後時間要往前取幾天  [default: 7]
  --skip-repetitive / --no-skip-repetitive
                                  是否要跳過重複類型的取關鍵字  [default: skip-repetitive]
  --help                          Show this message and exit.
```

### Trends
```shell
$ python main.py trend --help
Usage: main.py trend [OPTIONS] [KEYWORDS]...

  關鍵字流行比較，使用 Google Trends。

  注意請求次數過多會導致 ResponseError 429，最好搭配代理伺服器使用。

  Google 用 AI 辨識機器人啦 怎麼解= =

Arguments:
  [KEYWORDS]...  設定關鍵字list

Options:
  -s, --source-path TEXT       自訂輸入路徑及檔名
  -e, --end-date TEXT          熱度分析結束日期
  -n, --date-duration INTEGER  熱度分析的天數
  -t, --tournament TEXT        (錦標賽) 回傳的最熱門關鍵字數量， 必須為
                               {CHAMPION|FINAL|SEMI_FINAL|QUARTER_FINAL}。
                               CHAMPION: 回傳1個關鍵字。 FINAL: 回傳進入決賽關鍵字，1~5個。
                               SEMI_FINAL: 回傳進入半決賽關鍵字，6~25個。 QUARTER_FINAL:
                               回傳進入四分之一決賽關鍵字，26~225個。 預設為 FINAL
  --category INTEGER           Google Trends 的關鍵字類型。  [default: 0]
  --classification-mode TEXT   取檔模式  [default: keywords]
  --help                       Show this message and exit.
```

### Extract
```shell
$ python main.py extract --help                                                                                                
Usage: main.py extract [OPTIONS]

  文章提取。

Options:
  --topic TEXT                    選擇功能
  -s, --source-path TEXT          自訂輸入路徑  [default: ./assets/json]
  -d, --destination-path TEXT     自訂輸出路徑  [default: ./assets/article]
  -e, --end-date TEXT             取的最後時間
  -n, --date-duration INTEGER     最後時間要往前取幾天  [default: 7]
  -m, --classification-mode TEXT  選取文章模式  [default: keywords]
  --help                          Show this message and exit.

```

## Structure 專案結構說明
> Outdated version
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