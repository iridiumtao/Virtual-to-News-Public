import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import json
import re

import tensorflow.compat.v1 as tf
import numpy as np
import datetime
import uuid
import time
from os import listdir
from train.modeling import GroverModel, GroverConfig, samplef
from tokenization import tokenization
# from load import Generate_content
from backup import generate_articles
from random import sample
from others import txt_font, word, html, pic, title_produce

os.environ["CUDA_VISIBLE_DEVICES"] = '-1'

localtime = time.asctime(time.localtime(time.time()))
print("時間:", localtime)
##### ignore tf deprecated warning temporarily
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.DEBUG)
from tensorflow.python.util import deprecation

deprecation._PRINT_DEPRECATION_WARNINGS = False
try:
    from tensorflow.python.util import module_wrapper as deprecation
except ImportError:
    from tensorflow.python.util import deprecation_wrapper as deprecation
deprecation._PER_MODULE_WARNING_LIMIT = 0
#####

parser = argparse.ArgumentParser(description='Contextual generation (aka given some metadata we will generate articles')
parser.add_argument(
    '-metadata_fn',
    dest='metadata_fn',
    type=str,
    help='Path to a JSONL containing metadata',
)
parser.add_argument(
    '-out_fn',
    dest='out_fn',
    type=str,
    help='Out jsonl, which will contain the completed jsons',
)
parser.add_argument(
    '-input',
    dest='input',
    type=str,
    help='Text to complete',
)
parser.add_argument(
    '-config_fn',
    dest='config_fn',
    default='configs/mega.json',
    type=str,
    help='Configuration JSON for the model',
)
parser.add_argument(
    '-ckpt_fn',
    dest='ckpt_fn',
    default='../models/mega/model.ckpt',
    type=str,
    help='checkpoint file for the model',
)
parser.add_argument(
    '-target',
    dest='target',
    default='article',
    type=str,
    help='What to generate for each item in metadata_fn. can be article (body), title, etc.',
)
parser.add_argument(
    '-batch_size',
    dest='batch_size',
    default=1,
    type=int,
    help='How many things to generate per context. will split into chunks if need be',
)
parser.add_argument(
    '-num_folds',
    dest='num_folds',
    default=1,
    type=int,
    help='Number of folds. useful if we want to split up a big file into multiple jobs.',
)
parser.add_argument(
    '-fold',
    dest='fold',
    default=0,
    type=int,
    help='which fold we are on. useful if we want to split up a big file into multiple jobs.'
)
parser.add_argument(
    '-max_batch_size',
    dest='max_batch_size',
    default=None,
    type=int,
    help='max batch size. You can leave this out and we will infer one based on the number of hidden layers',
)
parser.add_argument(
    '-top_p',
    dest='top_p',
    default=0.95,
    type=float,
    help='p to use for top p sampling. if this isn\'t none, use this for everthing'
)
parser.add_argument(
    '-min_len',
    dest='min_len',
    default=1024,
    type=int,
    help='min length of sample',
)
parser.add_argument(
    '-eos_token',
    dest='eos_token',
    default=102,
    type=int,
    help='eos token id',
)
parser.add_argument(
    '-samples',
    dest='samples',
    default=5,
    type=int,
    help='num_samples',
)


def extract_generated_target(output_tokens, tokenizer):
    """
    Given some tokens that were generated, extract the target
    :param output_tokens: [num_tokens] thing that was generated
    :param encoder: how they were encoded
    :param target: the piece of metadata we wanted to generate!
    :return:
    """
    # Filter out first instance of start token
    assert output_tokens.ndim == 1

    start_ind = 0
    end_ind = output_tokens.shape[0]

    return {
        'extraction': tokenization.printable_text(''.join(tokenizer.convert_ids_to_tokens(output_tokens))),
        'start_ind': start_ind,
        'end_ind': end_ind,
    }


args = parser.parse_args()
proj_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
vocab_file_path = os.path.join(proj_root_path, "tokenization/clue-vocab.txt")
tokenizer = tokenization.FullTokenizer(vocab_file=vocab_file_path, do_lower_case=True)
news_config = GroverConfig.from_json_file(args.config_fn)

# We might have to split the batch into multiple chunks if the batch size is too large
default_mbs = {12: 32, 24: 16, 48: 3}
max_batch_size = args.max_batch_size if args.max_batch_size is not None else default_mbs[news_config.num_hidden_layers]

# factorize args.batch_size = (num_chunks * batch_size_per_chunk) s.t. batch_size_per_chunk < max_batch_size
num_chunks = int(np.ceil(args.batch_size / max_batch_size))
batch_size_per_chunk = int(np.ceil(args.batch_size / num_chunks))

# This controls the top p for each generation.
top_p = np.ones((num_chunks, batch_size_per_chunk), dtype=np.float32) * args.top_p

tf_config = tf.ConfigProto(allow_soft_placement=True)
tf_config.gpu_options.allow_growth = True
# ----------------
Input_path = "."
topic = ""
# 主題
print("1. 腸道, 2. 抗糖, 3. 業務技巧, 4. 心靈雞湯")
class_topics = input("輸入主題代碼: ")
# 設定參數
while True:
    if class_topics == "1":
        Input_path = 'Input/腸道'
        topic = "腸道"
        break
    elif class_topics == "2":
        Input_path = 'Input/抗糖'
        topic = "抗糖"
        break
    elif class_topics == "3":
        Input_path = 'Input/業務技巧'
        topic = "業務技巧"
        break
    elif class_topics == "4":
        Input_path = 'Input/心靈雞湯'
        topic = "心靈雞湯"
        break
    else:
        print("輸入錯誤,再輸入一次")
        print("1. 腸道, 2. 抗糖, 3. 業務技巧, 4. 心靈雞湯")
        class_topics = input("輸入主題代碼: ")
        continue
print(topic)
# 段落數
while True:
    paragraph = input("文章段落數: ")
    try:
        paragraph = int(paragraph)
        if isinstance(paragraph, int):
            break
    except Exception as e:
        print(e, "文章段落數: ")
        continue
Output_path = './Output/'
topic_path = './Input/base_topic_' + topic + '.txt'
files = listdir(Input_path)
print(files)
count = len(os.listdir(Input_path))
print("\nInput有", count, "篇文章")
for k in range(count):
    print("\n⬇️現在使用第", k + 1, "篇文章生成")
    # s = Generate_content(Generate_quantity=5, Input_path=Input_path, Output_path=Output_path, delete_index_weight=0.85, rela_index_weight=0.85, Article=files[k])
    # s = generate(Generate_quantity=10, Input_path='Input/腸道', Output_path='./Output/', Article='为何肠道健康如此重要.txt')
    try:
        s = generate_articles(Generate_quantity=args.samples + 1, Input_path=Input_path, Output_path=Output_path,
                              Article=files[k], path_basetopic=topic_path)
    except:
        print("Error!")
        continue

    constitute = list()
    # -----------------
    with tf.Session(config=tf_config, graph=tf.Graph()) as sess:
        initial_context = tf.placeholder(tf.int32, [batch_size_per_chunk, None])
        p_for_topp = tf.placeholder(tf.float32, [batch_size_per_chunk])
        eos_token = tf.placeholder(tf.int32, [])
        min_len = tf.placeholder(tf.int32, [])
        tokens, probs = samplef(news_config=news_config, initial_context=initial_context,
                                eos_token=eos_token, min_len=min_len, ignore_ids=None, p_for_topp=p_for_topp,
                                do_topk=False)

        saver = tf.train.Saver()
        saver.restore(sess, args.ckpt_fn)
        print('🍺Model loaded. \nInput something please:⬇️')

        content = str()
        sentences_used = paragraph
        # paragraph 不能大於samples
        for j in range(sentences_used):
            print("Now:", s[j])
            text = s[j]
            # -------------
            while text != "":
                for i in range(args.samples):
                    print("Sample,", i + 1, " of ", args.samples)
                    line = tokenization.convert_to_unicode(text)
                    bert_tokens = tokenizer.tokenize(line)
                    encoded = tokenizer.convert_tokens_to_ids(bert_tokens)
                    context_formatted = []
                    context_formatted.extend(encoded)
                    # Format context end

                    gens = []
                    gens_raw = []
                    gen_probs = []

                    for chunk_i in range(num_chunks):
                        tokens_out, probs_out = sess.run([tokens, probs],
                                                         feed_dict={initial_context: [
                                                                                         context_formatted] * batch_size_per_chunk,
                                                                    eos_token: args.eos_token, min_len: args.min_len,
                                                                    p_for_topp: top_p[chunk_i]})

                        for t_i, p_i in zip(tokens_out, probs_out):
                            extraction = extract_generated_target(output_tokens=t_i, tokenizer=tokenizer)
                            gens.append(extraction['extraction'])

                    l = re.findall('.{1,70}', gens[0].replace('[UNK]', '').replace('##', ''))
                    print("\n".join(l))

                    constitute.append("".join(l))
                text = ""
                print('Next try:⬇️')

            # -----------------------
        # 切割陣列 組合文章
        for k in range(sentences_used):
            globals()['sample' + str(k + 1)] = constitute[args.samples * k: args.samples * (k + 1)]

        for j in range(args.samples):
            # 隨機抽取文章
            rand = list()
            for sample_num in range(sentences_used):
                rand.append("".join(sample(globals()['sample' + str(sample_num + 1)], 1)))
            print(rand)

            today_date = str(datetime.date.today())
            now_time = str(time.strftime("%H-%M_", time.localtime()))
            uuid_sample = now_time + str(uuid.uuid1())

            # 簡體路徑
            Output_path = './Output/' + topic + '/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + "cht/"
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + today_date + '/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + uuid_sample + '/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + 'image/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path_cht = './Output/' + topic + '/cht/' + today_date + '/' + uuid_sample + '/'
            # 繁體路徑
            Output_path = './Output/' + topic + '/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + "zh/"
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + today_date + '/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + uuid_sample + '/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path = Output_path + 'image/'
            if not os.path.isdir(Output_path):
                os.mkdir(Output_path)
            Output_path_zh = './Output/' + topic + '/zh/' + today_date + '/' + uuid_sample + '/'

            output_file = open(Output_path_cht + uuid_sample + '.txt', 'w', encoding='utf-8')
            output_file.write("\n\n".join(rand))
            output_file.close()

            output_topic = open(Output_path_zh + '_Topic_' + uuid_sample + '.txt', 'w', encoding='utf-8')
            output_topic.write("\n\n".join(s))
            output_topic.close()

            txt_font(output_path_cht=Output_path_cht, output_path_zh=Output_path_zh, uuid_sample=uuid_sample)
            keyword = ""
            for c in range(sentences_used):
                keyword = keyword + " + " + s[c]

            pic(Output_path_cht=Output_path_cht + "image/", output_path_zh=Output_path_zh + "image/",
                uuid_sample=uuid_sample, keyword=topic + " + " + keyword, paragraph=paragraph)
            # HTML
            html(output_path=Output_path_zh, uuid_sample=uuid_sample)
            html(output_path=Output_path_cht, uuid_sample=uuid_sample)
            # WORD
            word(output_path=Output_path_zh, uuid_sample=uuid_sample)
            word(output_path=Output_path_cht, uuid_sample=uuid_sample)
            # 標題產生
            title_produce(output_path=Output_path_cht, uuid_sample=uuid_sample)
            title_produce(output_path=Output_path_zh, uuid_sample=uuid_sample)

localtime = time.asctime(time.localtime(time.time()))
print("時間:", localtime)
