# coding=utf-8
import warnings
warnings.filterwarnings(action='ignore',category=UserWarning,module='gensim')
import gensim
import os
import re
import sys
import json
import math
import pandas as pd
import numpy as np
import jieba
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from hanziconv import HanziConv


# jieba.set_dictionary('C:/Users/puppy/Documents/2020產學案-廣告文本生成/dict.txt')
w2v_path = './zh_wiki_word2vec_300.txt'
sw_path = './stopWords.txt' #./stopWords.txt

def Cut_sent(para):
    # para = re.sub('([。，！？/?])([^”’])', r"/1/n/2", para)
    para = re.sub('([。，！？/?])', r"/1/n/2", para)
    # para = re.sub('(/.{6})([^”’])', r"/1/n/2", para)
    # # para = re.sub('(/…{2})([^”’])', r"/1/n/2", para)
    # para = re.sub('([。！？/?][”’])([^，。！？/?])', r'/1/n/2', para)
    para = para.strip('/n')
    para = para.replace('/n/n','/n')

    return para.split("/n")


def Similarity(s1,s2):      #s1,s2 are lists, using the original similarity in paper
    count1 = len(s1)
    count2 = len(s2)
    common = [c for c in s1 if c in s2] #重複詞有差(method = Similarity)
    try:
        value = len(common)/(math.log(count1)+math.log(count2))
        # print('common:',common)
        # print('SimilarityValue:',value)
        # print('value:',value)
        # print('s1:',s1)
        # print('s2:',s2)
    except:
        value = 0
    return value


def Cosine_similarity(s1,s2,pretrained_model):
    def Combine_vector(vector_list):
        single_vector = [0 for i in range(300)]
        n = len(vector_list)
        for vector in vector_list:
            single_vector += (1/n)*vector
        return single_vector
    def Get_W2V(sentence,pretrained_model):
        vector_list = list()
        for word in sentence:
            try:
                vector_list.append(pretrained_model[word])
            except:
                pass
        return vector_list
    v1_list = Get_W2V(s1,pretrained_model)
    v2_list = Get_W2V(s2,pretrained_model) # v2 is a list of vector of words
    v1 = Combine_vector(v1_list)
    v2 = Combine_vector(v2_list)
    value = cosine_similarity([v1],[v2])
    return value[0][0]

def Tfidf_Similarity():
    pass

#篩選相關字詞排行 bert_w2v
def Create_edge_value_matrix(sentence_list,sen_rela_method = 0): #sentence_list is list of sentences
    n = len(sentence_list)
    edge_value_matrix = np.zeros((n,n),dtype = np.float64)
    if sen_rela_method == 1:
        embeddings_index = {}
        f = open(w2v_path,'r', encoding='utf8')
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()
    for i in range(n):
        for j in range(n):
            if i == j:
                edge_value_matrix[i][j] = 0
            else:
                if sen_rela_method == 0:
                    v = Similarity(sentence_list[i],sentence_list[j])
                    if v > 0: # Similarity > 0 (cosine > 0.5)
                        edge_value_matrix[i][j] = v
                elif sen_rela_method == 1:
                    v = Cosine_similarity(sentence_list[i],sentence_list[j],embeddings_index)
                    if v > 0.6: # Similarity > 0 (cosine > 0.5)
                        edge_value_matrix[i][j] = v
                else:
                    print('error method NO.')
                    sys.exit()


    return edge_value_matrix

def sentence_weight(num_of_sen,edge_value_matrix): #based on textrank algorithm
    vertex_weight_list = [1 for i in range(num_of_sen)] #initialize WS


    stop = 1
    d = 0.85
    while stop != 0:
        pre_vertex_weight_list = vertex_weight_list.copy()
        for i in range(num_of_sen):
            relation = 0
            in_vertex = list()
            for vertex in range(len(edge_value_matrix[i])):
                if edge_value_matrix[i][vertex] > 0:
                    in_vertex.append(vertex)
            for vertex in in_vertex:
                relation += ((edge_value_matrix[i][vertex]/sum(edge_value_matrix[vertex]))*vertex_weight_list[vertex]) #vetexn has relationship with other vertex
            vertex_weight_list[i] = (1-d) + d*(relation)
        for check in range(num_of_sen):
            if abs(pre_vertex_weight_list[check]-vertex_weight_list[check]) < 0.0001:
                stop = 0
                break
    return vertex_weight_list

def Cut_content(sentence_list):     # Create_sentence_list(with or without stopwords)
    content_cut_in_sen = list()
    content_cut_in_sen_stop = list()
    stopWords = list()
    for sen in sentence_list:
        sen_cut_in_words = list()
        sen_cutted = jieba.cut(sen,cut_all=False)
        # print(sen_cutted)
        for word in sen_cutted:
            word = word.strip()
            if word:
                sen_cut_in_words.append(word)


        with open(sw_path, 'r', encoding='UTF-8') as file: #https://github.com/goto456/stopwords/blob/master/cn_stopwords.txt
            for data in file.readlines():
                data = data.strip()
                stopWords.append(data)
        remain = list(filter(lambda a: a not in stopWords and a != '/n', sen_cut_in_words))
        if remain:
            content_cut_in_sen.append(sen_cut_in_words)
            content_cut_in_sen_stop.append(remain)

    return content_cut_in_sen,content_cut_in_sen_stop

def Summarization(text,sen_len,sen_rela_method,key_sen='', delete_index_weight=0., rela_index_weight=0.):
    suma = list()

    cut_content_list = Cut_sent(text)                         #cut text to sentence
    print('cut_content_list:',cut_content_list)
    if key_sen:
        cut_content_list.append(key_sen)
    # print('next:',cut_content_list)
    ct,cts = Cut_content(cut_content_list) # cut sentence,cut sentence stopWords(remain)
    matrix = Create_edge_value_matrix(cts,sen_rela_method)
    vw = sentence_weight(len(cts),matrix)
    df = pd.DataFrame()
    df['ct'] = ct ; df['cts'] = cts ; df['vw'] = vw
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    # pd.concat((df['cts'],df['vw']), axis=1)
    # print(df)
    if key_sen:
        df = df.drop(df.tail(1).index)                            #drop key_sen
    # print(len(matrix),len(df),len(cts))
    sort_df = df.sort_values('vw',ascending=False)
    # print(sort_df)
    first_index = sort_df.index[0]
    # print(matrix[first_index][0])
    if sen_rela_method == 0:
        delete_index = [i for i in range(len(df)) if matrix[first_index][i]>delete_index_weight]
    elif sen_rela_method == 1:
        delete_index = [i for i in range(len(df)) if matrix[first_index][i]>delete_index_weight]
    suma_index = [first_index]
    for i in range(1,len(sort_df)):
        if len(suma_index) == sen_len:
            break
        if sort_df.index[i] in delete_index:
            continue
        else:
            suma_index.append(sort_df.index[i])
            if sen_rela_method == 0:
                rela_index = [j for j in range(len(df)) if matrix[sort_df.index[i]][j]>rela_index_weight]
            elif sen_rela_method == 1:
                rela_index = [j for j in range(len(df)) if matrix[sort_df.index[i]][j]>rela_index_weight]
            for k in rela_index:
                if k not in delete_index:
                    delete_index.append(k)
            # print('delete sentence:',delete_index)
    #suma_index = sorted(suma_index)
    print(suma_index)
    print(len(suma_index))
    for i in suma_index:
        suma.append(''.join(sort_df.loc[i]['ct']))
    #return(''.join(suma))
    return(suma)

def Generate_content(Generate_quantity, Input_path, Output_path, delete_index_weight, rela_index_weight, Article):
    content = str()
    print("目前文章:" + Article)
    print("start:載入中")
    file = open(Input_path + '/' + Article, 'r', encoding = 'utf-8')
    file = HanziConv.toSimplified(file.read())
    content += file

    s = Summarization(text = content, sen_len = int(Generate_quantity), sen_rela_method=0, key_sen='', delete_index_weight=delete_index_weight, rela_index_weight=rela_index_weight)
    
    #sen rela method = 1 功能未知
    for i in range(Generate_quantity):
        # print('before:',s[i])
        s[i] = s[i].strip().strip('/2').strip('/1')
        # print('after:',s[i])
    #移除空白
    for i in range(Generate_quantity):
        try:
            s.remove("")
        except:
            pass
    print("現有句數:" , len(s))
    for i in range(len(s)):
        print(s[i])
    print(s)
    return s

Generate_content(Generate_quantity=10, Input_path='Input/腸道', Output_path='./Output/', delete_index_weight=0.85, rela_index_weight=0.85, Article='为何肠道健康如此重要.txt')
