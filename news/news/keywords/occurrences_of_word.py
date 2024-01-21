import os

import pandas as pd

# 確保不會重複取


def useds_and_need(files, used_file_path, rest):
    if not rest and os.path.isfile(used_file_path):
        used_file = pd.read_csv(used_file_path)['used_file'].tolist()
        need_files = []
        for file in files:
            if file.replace('\\\\', '\\') not in used_file:
                need_files.append(file)
        used_file.extend(need_files)
    else:
        used_file = files
        need_files = files

    return used_file, need_files


def get_contents(need_files, name):
    # 取資料2
    contents_sentences = []
    # 每個檔案裡面有幾篇文章
    several_articles = []
    for file in need_files:
        words_all_filters = pd.read_json(file).transpose()[name]
        contents_sentences.extend(words_all_filters)
        several_articles.append(len(words_all_filters))
    # 取資料1
    # contents_sentences = pd.concat((pd.read_json(file).transpose(
    # )['words_all_filters'] for file in files), ignore_index=True)

    # 保留轉換寫法
    # contents_single_word = []
    # for word in tf_dict:
    #     contents_single_word.append(list(word.keys()))
    return contents_sentences, several_articles


def occurrences_of_word_dict(occurrences_of_word_path, rest):
    if not rest and os.path.isfile(occurrences_of_word_path):
        occurrences_of_word = pd.read_json(occurrences_of_word_path)[
            'Qunatity'].to_dict()
    else:
        occurrences_of_word = {}

    return occurrences_of_word


def calculate_occurrences_of_word(contents_sentences, occurrences_of_word):
    for content_sentences in contents_sentences:
        word_dict = {}
        # for sentence_words in content_sentences:
        for word in content_sentences:
            if word not in word_dict.keys():
                word_dict[word] = 1
        for word in word_dict.keys():
            # print(word)
            if word in occurrences_of_word:
                occurrences_of_word[word] += 1
            else:
                occurrences_of_word[word] = 1

    return occurrences_of_word

def sentence_calculate_occurrences_of_word(contents_sentences, occurrences_of_word):
    for content_sentences in contents_sentences:
        word_dict = {}
        for sentence_words in content_sentences:
            for word in sentence_words:
                if word not in word_dict.keys():
                    word_dict[word] = 1
        for word in word_dict.keys():
            # print(word)
            if word in occurrences_of_word:
                occurrences_of_word[word] += 1
            else:
                occurrences_of_word[word] = 1

    return occurrences_of_word


def test(occurrences_of_word, quantity, target):
    target_quantity = occurrences_of_word[target]
    bigger_target = {}
    bigger_val = {}
    val = quantity*0.1
    for o, v in occurrences_of_word.items():
        if v > target_quantity:
            bigger_target[o] = v
        if v > val:
            bigger_val[o] = v

    print(f'bigger_target:{bigger_target}')
    print()
    print(f'bigger_val:{bigger_val}')
    print()
    print(f'val:{val}')


def occurrences_of_word(files, field_name, assets, rest):
    if not os.path.isdir(assets):
        os.mkdir(assets)
    used_files_path = assets+'/used_files.csv'  # 已使用檔案名稱的檔案
    occurrences_of_word_path = assets+'/occurrences_of_word.json'  # 單詞出現次數檔案

    # 確保不會重複取，如果不存在，則全部都需要處理
    used_files, need_files = useds_and_need(files, used_files_path, rest)

    # 儲存已使用
    df_used_files = pd.DataFrame(used_files, columns=['used_file'])
    df_used_files.to_csv(used_files_path, index=False)

    # 取的內容，取得文章的數量
    contents_sentences, several_articles = get_contents(need_files, field_name)

    # 儲存文章的數量
    df_several_articles = pd.DataFrame(
        several_articles, columns=['several_articles'])
    df_used_files = pd.read_csv(used_files_path)
    used_files_and_several_articles = pd.concat(
        [df_used_files, df_several_articles], axis=1)
    used_files_and_several_articles.to_csv(used_files_path, index=False)

    # 讀取 單詞出現次數 檔案，若無則傳送
    occurrences_of_word = occurrences_of_word_dict(
        occurrences_of_word_path, rest)

    # 計算全部文章單詞出現在幾篇文章
    if field_name == 'contents_word_segmenter':
        new_occurrences_of_word = calculate_occurrences_of_word(
            contents_sentences, occurrences_of_word)
    elif field_name == 'contents_all_filters':
        new_occurrences_of_word = sentence_calculate_occurrences_of_word(
            contents_sentences, occurrences_of_word)

    # 儲存
    df_occurrences_of_word = pd.DataFrame.from_dict(
        new_occurrences_of_word, orient='index').rename(columns={0: 'Qunatity'})
    df_occurrences_of_word.to_json(occurrences_of_word_path, force_ascii=False)

    # 測試查看頻率較高數值
    # test(occurrences_of_word=new_occurrences_of_word,
    #      quantity=sum(several_articles), target='台積電')


if __name__ == '__main__':
    occurrences_of_word()
