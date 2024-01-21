# coding=utf8
import re

import cn2an
from opencc import OpenCC

from news.common.file_management import FileManagement
from news.extract.util import Filter
from news.keywords.article_analyzer import ArticleAnalyzer


def empty(text):
    """
    回傳無除空白和除空白
    """
    return text and text.strip()


def combine(sentences: list, num: int):
    """
    組合句子，不要大於10個字
    """
    new_sentences = []
    new_words = ''
    for s in sentences:
        new_words += s
        # 超過10個字就刷新並加入句子表
        if len(new_words) + len(s) >= num:
            new_sentences.append(new_words)
            new_words = ''
    # 結尾剛好10，不要加入句子
    if new_words != '':
        new_sentences.append(new_words)
    return new_sentences


def transcript(article: str, num: int, filename: str, destination_path: str):
    """
    生成講稿並儲存
    """
    # 句子過濾
    results = re.compile(r'％', re.S)
    article = re.sub(results, '%', article)
    results = re.compile(r',', re.S)
    article = re.sub(results, '', article)
    results = re.compile(r'[（](.*?)[）]', re.S)
    article = re.sub(results, '', article)
    results = re.compile(r'[(](.*?)[)]', re.S)
    article = re.sub(results, '', article)
    # article = Filter.parenthesis(article)
    results = re.compile(r'\n', re.S)
    article = re.sub(results, '', article)
    results = re.compile(r'。', re.S)
    article = re.sub(results, '。。', article) # 為了後面分段可以多共一格

    # 數字轉中文
    chinese_article = cn2an.transform(article, 'an2cn')
    # 簡體轉繁體
    traditional_article = OpenCC('s2t').convert(chinese_article)
    # 句子切割
    sentence_delimiters = ['?', '!', ';', '？', '！', '；', '……', '…', '\n', '，', '、']
    sentences = Filter.delimiters([traditional_article], sentence_delimiters)
    # 去除空值
    sentences_no_null = list(filter(empty, sentences))
    # 句子切割
    sentence_delimiters = ['。']
    sentences = Filter.delimiters(sentences_no_null, sentence_delimiters)

    # 切詞
    sentences_word_segmenter = ArticleAnalyzer(content_list=sentences).word_segmenter()
    # 組合
    sentences_combine = []
    for i, s in enumerate(sentences):
        # 沒超過的句子就不組合了
        if len(s) > num:
            combine_words = combine(sentences_word_segmenter[i], num)
        else:
            combine_words = [s]
        sentences_combine.extend(combine_words)
    content = "\n".join(sentences_combine)

    FileManagement.save_extract(filename=filename,
                                destination_path=destination_path,
                                content=content)
    return content


def main():
    article = '主題是疫苗。\n根據中國國家衛健委的數據，60歲以上中國人，\
只有大約64%的人接種3劑。外媒引述大陸官方數據報導，中國15歲以上人口中，\
約有3.75億人尚未接種三劑，單日接種率已降至每天80萬以下。指揮中心表示，\
目前家用快篩試劑數量充足，但因應滿6個月至5歲幼兒施打作業尚未進行，\
指揮中心建議自7月1日起，實施第二輪學齡前兒童（0至6歲）免費再領取一份五劑快篩試劑。\
換言之，兩種mRNA都將開放給所有年紀在6個月以上的美國人接種。清零政策越來越像是一個負擔\
，呈現的風險已經大過於好處，會影響中國自身及全球經濟復甦。華爾街最著名的空頭之一認為，\
在美股拋售重新開始前，目前的漲勢將繼續擴大。新變種病毒擴散延遲疫情緩和時點，\
持續影響服務業復甦。徐之強進一步指出，台灣央行於3月升息1碼後，\
6月轉為升息半碼並搭配存準率調整，主要因服務業受疫情衝擊且利率已處於較高水準。\
那斯達克綜合指數下跌93.6點或0.81%，暫報11,514.02點。美國5月季調後成屋簽約銷售指數月增率報0.7%，\
預期-3.7%，前值-4.0%。費半下跌16.91點或0.62%，暫報2,701.56點。\
談到影響2022年後市的經濟成長與金融情勢的主要因素，徐之強點出要看六大面向，\
分別為：COVID-19變種病毒風險、中國本土疫情再起使官方再度大規模封城、與口服藥物更加普及。'

    article = '疫苗。指揮中心表示，目前家用快篩試劑數量充足，\
但因應滿6個月至5歲幼兒施打作業尚未進行，指揮中心建議自7月1日起，\
實施第二輪學齡前兒童（0至6歲）免費再領取一份五劑快篩試劑。\
影響後市的經濟成長與金融情勢的主要要看疫情等，6，大因素。\
華爾街最著名的空頭之一認為，在美股拋售重新開始前，目前的漲勢將繼續擴大。\
此外，國光生技流感過去市場主要在北半球，每年根據世界衛生組織（WHO）最新公布的病毒株，\
上半年生產流感，下半年供貨海外市場。國內疫情自4月中旬起竄燒，5月確診人數節節攀高，\
產險業預期理賠高峰期將落在6、7月，引起外界關注產險公司現金流量是否拉警報。\
徐之強進一步指出，台灣央行於，3，月升息，1，碼後，6，月轉為升息半碼並搭配存準率調整，\
主要因服務業受疫情衝擊且利率已處於較高水準。(5)，新變種病毒擴散延遲疫情緩和時點，\
持續影響服務業復甦。國內疫情仍屬於社區廣泛流行狀態，不過近一週新增本土病例數呈穩定下降趨勢，中重症病例數減少。'

    content = transcript(article, 10, filename='test', destination_path='./assets/article')


if __name__ == '__main__':
    main()