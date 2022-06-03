from vectorizer import Vectorizer
from scipy import spatial
from harvesttext import HarvestText
from hanziconv import HanziConv
import re
import random
import pandas as pd

def ranking(topic,articles,quantity,senten):
    rk={
        "vector":[],
        "sentence":[]
    }

    i=0
    for article in articles:
        if len(senten[i]) > 10 :
            rk["vector"].append(spatial.distance.cosine(topic,article))
            rk["sentence"].append(senten[i])
            i+=1
        else:
            i+=1
            continue
    rank=pd.DataFrame.from_dict(rk)
    rank.sort_values("vector",inplace=True,ascending=True)

    print("搜尋到{0}個語句，將以排行前{1}句產出文章。".format(len(rank),quantity))
    print(rank[0:quantity])
    return rank["sentence"]

def random_base(base):
    ht=HarvestText()
    base = HanziConv.toSimplified(base.read())
    base_topic = ht.clean_text(base)
    base_topic = ht.cut_paragraphs(base_topic,num_paras=10)
    random.seed()
    print("Import topic quantity:",len(base_topic))
    return base_topic[random.randint(0,len(base_topic)-1)]

def generate_articles(Generate_quantity, Input_path, Output_path,Article,path_basetopic):
    content = str()
    print("目前文章:" + Article)
    print("Loading...")
    file = open(Input_path + '/' + Article, 'r', encoding = 'utf-8-sig')
    file = HanziConv.toSimplified(file.read())

    ht=HarvestText()
    sentences=ht.clean_text(file,remove_url=False)
    sentences=ht.cut_paragraphs(sentences)
    results = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=_%#:]*', re.S)

    for st in sentences:
        sentences[sentences.index(st)] = re.sub(results,'',st)

    sentences[0]=random_base(open(path_basetopic, 'r', encoding = 'utf-8-sig'))
    print("Topic: ",sentences[0])
    vectorizer = Vectorizer()
    vectorizer.bert(sentences)
    vectors = vectorizer.vectors
    r = ranking(vectors[0],vectors[1:],Generate_quantity,sentences[1:])
    return list(r[0:Generate_quantity])



# g = generate_articles(Generate_quantity=10, Input_path='Input/腸道', Output_path='./Output/', Article='为何肠道健康如此重要.txt')
# print(g)
