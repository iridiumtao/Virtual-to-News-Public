import os
import re

import numpy as np
import pandas as pd
import torch
import transformers
from scipy.spatial.distance import cosine

# from sentence_transformers import SentenceTransformer

sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '\n']


class Filter():
    def __init__():
        pass

    def all(articles, sentence_delimiters, topic):
        no_repetition_articles = list(set(articles))

        parenthesis_articles = Filter.parenthesis(no_repetition_articles)

        intrasentences_cutting_delimiters = Filter.delimiters(
            parenthesis_articles, sentence_delimiters)
        # no_repetition_sentences = list(set(intrasentences_cutting_delimiters))

        intrasentences_cutting = Filter.too_many_words(
            intrasentences_cutting_delimiters, 100)
        no_repetition_sentences = list(set(intrasentences_cutting))

        word_count_filter = [
            s.strip() for s in no_repetition_sentences
            if len(s.strip()) > 0 and len(s.strip()) < 100
        ]

        word_substitution = Filter.word_substitution(word_count_filter)
        no_repetition_sentences = list(set(word_substitution))
        # sentences=no_repetition_sentences
        sentences = Filter.word_exclusion(topic, word_substitution)
        return sentences

    def parenthesis(articles):
        # results = re.compile(r'[「](.*?)[」]', re.S)
        # for i, article in enumerate(articles):
        #     for comma in re.findall(results, article):
        #         if '，' in comma:
        #             articles[i] = article.replace(comma, '')
        #             articles.append(comma)
        results = re.compile(r'[「]', re.S)
        articles = [re.sub(results, '', art) for art in articles]
        results = re.compile(r'[」]', re.S)
        articles = [re.sub(results, '', art) for art in articles]

        results = re.compile(r'[(](.*?)[)]', re.S)
        articles = [re.sub(results, '', art) for art in articles]
        return articles

    def delimiters(articles, sentence_delimiters):
        intrasentences_cutting_delimiters = []
        for article in articles:
            sentence_cutting = [article]
            for delimiters in sentence_delimiters:
                text, sentence_cutting = sentence_cutting, []
                for t in text:
                    sentence_cutting += t.split(delimiters)
            intrasentences_cutting_delimiters.extend(sentence_cutting)
        return intrasentences_cutting_delimiters

    def too_many_words(sentences, chars):
        intrasentences_cutting = sentences
        for sentence in sentences:
            if len(sentence) > chars:
                r_list = sentence.split('，')
                num = len(r_list)
                clist = []
                # stemp=3
                # if num > 3:
                #     for i in range(0, num, 3):
                #         if num-i-3 >= 0:
                #             clist.append(r_list[i]+'，'+r_list[i+1]+'，'+r_list[i+2])
                #         elif num-i-2 == 0:
                #             clist.append(r_list[i]+'，'+r_list[i+1])
                #         elif num-i-1 == 0:
                #             clist.append(r_list[i])
                clist = r_list
                sentence_location = intrasentences_cutting.index(sentence)
                del intrasentences_cutting[sentence_location]
                for c in clist:
                    intrasentences_cutting.extend(c)
        return intrasentences_cutting

    def word_substitution(sentences):
        results = re.compile(r' ', re.S)
        sentences = [re.sub(results, '_', st) for st in sentences]
        results = re.compile(r'\s', re.S)
        sentences = [re.sub(results, '', st) for st in sentences]
        # sentences = re.sub(results, '，', sentences)

        # results1 = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=_%#:]*', re.S) # 網址
        results2 = re.compile(r'，', re.S)
        # results3 = re.compile(r'^\d*\.', re.S) # 任意数字，等價於 [0-9]  ^開頭
        # results4 = re.compile(r'\([\d]*\)', re.S)

        # results5 = re.compile(r'\W.*.*\W', re.S) #非字母数字及下划线
        # results6 = re.compile(r'\s', re.S) # 任意空白字符

        # for st in sentences:
        #     sentences[sentences.index(st)] = re.sub(results1, '', st)
        # for st in sentences:
        #     sentences[sentences.index(st)] = re.sub(results3, '', st)

        # for st in sentences:
        #     sentences[sentences.index(st)] = re.sub(results4, '', st)

        # for st in sentences:
        #     sentences[sentences.index(st)] = re.sub(results6, '', st)

        for st in sentences:
            sentences[sentences.index(st)] = re.sub(results2, ' ', st)
        # for st in sentences:
        #     sentences[sentences.index(st)] = re.sub(results5, '', st)
        return sentences

    def word_exclusion(topic, sentences):
        # 排除主題文字
        new_sentences = []
        sentences_append = new_sentences.append
        results = re.compile(topic, re.S)
        for i in sentences:
            sentences_append(re.sub(results, '', i) if topic in i else i)
            # if topic in i:
            #     sentences_append(re.sub(results, '', i))
            # # elif '本文' in i or '來源：'in i or '譯者：'in i or '圖：'in i:
            # #     pass
            # else:
            #     sentences_append(i)
        return new_sentences

    def content_conversion(content):
        results = re.compile(r'\s', re.S)
        content = re.sub(results, '，', content)
        results = re.compile(r'_', re.S)
        content = re.sub(results, ' ', content)
        day = ['今天', '今日', '昨日', '昨天']
        for d in day:
            results = re.compile(d, re.S)
            content = re.sub(results, '', content)
        return content


def ranking(topic, articles, quantity, sentence):
    rk = {"vector": [], "sentence": []}
    vector_append = rk["vector"].append
    sentence_append = rk["sentence"].append
    i = 0
    for article in articles:
        if len(sentence[i]) > 10:
            vector_append(cosine(topic, article))
            sentence_append(sentence[i])
            i += 1
        else:
            i += 1
            continue
    rank = pd.DataFrame.from_dict(rk)
    rank.sort_values("vector", inplace=True, ascending=True)
    return rank["sentence"].tolist()[0:quantity]


def ranking3(topic, articles, quantity, sentence):
    rk = {"vector": [], "sentence": []}
    vector_append = rk["vector"].append
    sentence_append = rk["sentence"].append
    i = 0
    len_topic = len(topic)
    start = int(len_topic / 2)
    end = len_topic - start
    for article in articles:
        vector_append(cosine(topic[end:], article[:start]))
        sentence_append(sentence[i])
        i += 1
    rank = pd.DataFrame.from_dict(rk)
    rank.sort_values("vector", inplace=True, ascending=True)
    return rank["sentence"].tolist()[0:quantity]


def ranking2(topic, articles, senten):
    rk = {"vector": [], "sentence": []}

    i = 0
    for article in articles:
        if len(senten[i]) > 10:
            rk["vector"].append(cosine(topic, article))
            rk["sentence"].append(senten[i])
            i += 1
        else:
            i += 1
            continue
    rank = pd.DataFrame.from_dict(rk)
    rank.sort_values("vector", inplace=True, ascending=True)
    return rank.iloc[1, 1]


class Vectorizer:
    def __init__(self):
        self.vectors = []

    def bert_many_sentences(sentence_list, vectors: list, batch: int,
                            vector_num: int):
        if len(sentence_list) > vector_num:
            vectorizer = Vectorizer()
            vectorizer.bert(sentence_list[vector_num:vector_num + batch])
            vectors.extend(vectorizer.vectors)
            vector_num += batch
            return Vectorizer.bert_many_sentences(sentence_list, vectors,
                                                  batch, vector_num)
        else:
            return vectors

    def bert(self, sentences, pretrained_weights='./assets/model/ckiplab/bert-base-chinese'):
        if not os.path.isdir(pretrained_weights):
            pretrained_weights = 'ckiplab/bert-base-chinese'
        device = torch.device('cuda', 0)
        tokenizer = transformers.BertTokenizer.from_pretrained(
            pretrained_weights)
        model = transformers.AutoModelForMaskedLM.from_pretrained(
            pretrained_weights).to(device)
        tokenized = list(
            map(lambda x: tokenizer.encode(x, add_special_tokens=True),
                sentences))
        max_len = 0
        for i in sentences:
            if len(i) > max_len:
                max_len = len(i)
        padded = np.array([
            i * (max_len // len(i)) + i[:(max_len % len(i))] for i in tokenized
        ])
        # padded = np.array([i + [0] * (max_len - len(i)) for i in tokenized])
        padded = torch.from_numpy(padded).clone().detach()
        input_ids = torch.as_tensor(padded, device=device)  #torch.tensor
        with torch.no_grad():
            last_hidden_states = model(input_ids)
        torch.cuda.empty_cache()
        vectors = last_hidden_states[0][:, 0, :].cpu().numpy()
        self.vectors = vectors

    def sentences_combination(sentences: list, first, few_sentences: int = 10):
        new = ''
        sentences.insert(0, first)
        embeddings = Vectorizer.sentencetransformer(sentences).tolist()
        sentence_embeddings = embeddings[1:]
        first_embeddings = embeddings[0]
        first = ranking3(first_embeddings, sentence_embeddings[:], 2,
                         sentences)[0]
        if few_sentences > len(embeddings):
            few_sentences = int(len(embeddings) / 2)
        for _ in range(few_sentences, 0, -1):
            new = new + first + '。'
            first_embeddings = sentence_embeddings[sentences.index(first)]
            sentence_embeddings.pop(sentences.index(first))
            sentences.remove(first)
            first = ranking3(first_embeddings, sentence_embeddings[:], 2,
                             sentences)[0]
        return new

    # def sentencetransformer2(sentences,pretrained_weights='paraphrase-distilroberta-base-v1'):
    #     model = SentenceTransformer(pretrained_weights)
    #     sentence_embeddings=model.encode(sentences)
    #     return sentence_embeddings.tolist()

    def sentencetransformer(sentences,
                            pretrained_weights='./assets/model/ckiplab/bert-base-chinese'):
        if not os.path.isdir(pretrained_weights):
            pretrained_weights = 'ckiplab/bert-base-chinese'
        tokenizer = transformers.BertTokenizer.from_pretrained(
            pretrained_weights)
        max_len = 0
        for i in sentences:
            if len(i) > max_len:
                max_len = len(i)
        tokenized = list(
            map(lambda x: tokenizer.encode(x, add_special_tokens=True),
                sentences))
        padded = np.array([
            i * (max_len // len(i)) + i[:(max_len % len(i))] for i in tokenized
        ])
        return padded
