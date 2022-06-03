from typing import List

from vectorizer import Vectorizer
from scipy import spatial
from harvesttext import HarvestText
from hanziconv import HanziConv
import re
import random
import pandas as pd
from pathlib import Path


def ranking(topic, articles, quantity, senten):
    rk = {
        "vector": [],
        "sentence": []
    }

    i = 0
    for article in articles:
        #if len(senten[i]) > 10:
        # 長度改段以便測試
        if len(senten[i]) > 3:
            rk["vector"].append(spatial.distance.cosine(topic, article))
            rk["sentence"].append(senten[i])
            i += 1
        else:
            i += 1
            continue
    rank = pd.DataFrame.from_dict(rk)
    rank.sort_values("vector", inplace=True, ascending=True)

    print("搜尋到{0}個語句，將以排行前{1}句產出文章。".format(len(rank), quantity))
    print(rank[0:quantity])
    return rank["sentence"]


def random_base(base: List[str]):  # 不確定type，先放str list看看
    ht = HarvestText()
    base = HanziConv.toSimplified(base)
    base_topic = ht.clean_text(base)
    base_topic = ht.cut_paragraphs(base_topic, num_paras=10)
    random.seed()
    print("Import topic quantity:", len(base_topic))
    return base_topic[random.randint(0, len(base_topic) - 1)]


def generate_articles(Generate_quantity, Input_path, Output_path, Article):
    content = str()
    print("目前文章:" + Article)
    print("Loading...")
    file = open(Input_path + '/' + Article, 'r', encoding='utf-8-sig')
    file = HanziConv.toSimplified(file.read())

    ht = HarvestText()
    sentences_str = ht.clean_text(file, remove_url=False)
    # sentences = ht.cut_paragraphs(sentences_str)
    # 測試分11斷
    sentences = ht.cut_paragraphs(sentences_str, num_paras=16, remove_puncts=False)

    results = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=_%#:]*', re.S)

    for st in sentences:
        sentences[sentences.index(st)] = re.sub(results, '', st)

    # 暫時
    topic = ["餐點好吃嗎"]
    # sentences[0] = random_base(topic)

    # 插入 list 最前面 to conform 後面的 code
    sentences.insert(0, random_base(topic))
    print("Topic: ", sentences[0])

    vectorizer = Vectorizer()
    vectorizer.bert(sentences)
    vectors = vectorizer.vectors
    r = ranking(vectors[0], vectors[1:], Generate_quantity, sentences[1:])

    # 轉成繁體(易於閱讀)寫入到檔案
    path = 'output.txt'
    Path("output/").mkdir(parents=True, exist_ok=True)
    with open("output/" + path, 'w+', encoding='utf-8') as f:
        text_list = list(r[0:Generate_quantity])
        trad_text_list = []
        for text in text_list:
            trad_text_list.append(HanziConv.toTraditional(text))
        f.write('\n'.join(trad_text_list) + '\n')
        f.close()
        return list(r[0:Generate_quantity])


if __name__ == '__main__':
    g = generate_articles(Generate_quantity=20, Input_path='input', Output_path='output', Article='input.txt')
    print(g)
