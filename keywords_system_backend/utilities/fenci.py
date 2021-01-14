#!/usr/bin/env python3

import sys
import os
import re
import json
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from pymongo.errors import AutoReconnect, DuplicateKeyError, BulkWriteError
import urllib
import math
import jieba
import pickle
from jieba.analyse.textrank import TextRank, UndirectWeightedGraph
from jieba.posseg import pair
from collections import defaultdict
from operator import itemgetter
from database.db_basic import  client

coll = None
user_coll = None
invalid_coll = None
stop_coll = None
count = None


def text_dehtml(text):
    # 依次为：html注释、html tag、html entity、残缺的html属性配置串、URL
    tag_re = re.compile(
        r'(<!--.*?-->|<[^>]*>|&[\w#\d]{2,5}($|;|\s)|<\w+[\s\w"\'\d=:!;%#/-]+|(http|ftp|https):\/\/[\w:;\d#%\.=\?\/-]+)')
    space_re = re.compile(r'\s+')
    text = tag_re.sub('', text)
    return space_re.sub(' ', text)


# 把mongo里全站爬取的数据提取成纯文本形式的数组
def text_load_from_mongo(_id):
    doc_list = []
    doc = coll.find_one({'_id': ObjectId(_id)})
    title = doc.get('title', '')
    desc = doc.get('description', '')
    keywords = doc.get('keywords', '')
    content = doc.get('body', '')
    doc_text = "{}.{}.{}.{}".format(title, desc, keywords, content)
    doc_category = doc.get('category', '')
    doc_list.append({
        'category': doc_category,
        'text': text_dehtml(doc_text)
    })
    #print("{} docs loaded".format(len(doc_list)))
    return doc_list


class WordGroupRank(TextRank):

    def cut_sent(self, para):
        para = re.sub('([。！？\?：，,；;]|\.{6}|…{2})', r"\n", para)  # 单字符断句符
        para = para.rstrip()  # 段尾如果有多余的\n就去掉它
        return para.split("\n")

    def pairfilter(self, wp):
        return (wp.flag in self.pos_filt
                and wp.word.lower() not in self.stop_words)

    def set_stop_words_form_mongo(self, stop_coll,invalid_coll):
        all_stop_words = stop_coll.find()
        for stop_word in all_stop_words:
            word = stop_word['word']
            self.stop_words.add(word)
        
        # 将stop word和 invalid word 合在一起
        all_invalid_words = invalid_coll.find()
        for invalid_word in all_invalid_words:
            word = invalid_word['word']
            self.stop_words.add(word)
        #print('not',self.stop_words)

    def text_map(self, document, allowPOS=('ns', 'n', 'vn', 'v')):
        """
        Extract keywords from sentence using TextRank algorithm.
        Parameter:
            - topK: return how many top keywords. `None` for all possible words.
            - withWeight: if True, return a list of (word, weight);
                          if False, return a list of words.
            - allowPOS: the allowed POS list eg. ['ns', 'n', 'vn', 'v'].
                        if the POS of w is not in this list, it will be filtered.
            - withFlag: if True, return a list of pair(word, weight) like posseg.cut
                        if False, return a list of words
        """
        category = document['category']
        doc_text = document['text']
        #print("cutting and words grouping")

        self.pos_filt = frozenset(allowPOS)
        words_per_length = {}
        # cut text into sentences
        sentences = self.cut_sent(doc_text)
        for sentence in sentences:
            try:
                #print([wp for wp in self.tokenizer.cut(sentence)])
                sentence_words = [wp for wp in self.tokenizer.cut(
                    sentence) if self.pairfilter(wp)]
                for sentence_word in sentence_words:
                    word_length = len(sentence_word.word)
                    if word_length not in words_per_length:
                        words_per_length[word_length] = [sentence_word.word]
                    else:
                        words_per_length[word_length].append(
                            sentence_word.word)
                for group_length in range(2, 4):
                    for i, wp in enumerate(sentence_words):
                        if i+group_length > len(sentence_words):
                            break
                        group = sentence_words[i:i+group_length]
                        group_flag = 'v' if 'v' in [
                            _wp.flag[0] for _wp in group] else 'n'
                        group_word = "".join([_wp.word for _wp in group])
                        group_pair = pair(group_word, group_flag)
                        group_word_length = len(group_pair.word)
                        if group_word_length not in words_per_length:
                            words_per_length[group_word_length] = [
                                group_pair.word]
                        else:
                            words_per_length[group_word_length].append(
                                group_pair.word)
            except Exception as e:
                print("error processing document: {}".format(e))
        return words_per_length


# 处理标题和摘要，提取关键词
def text_map(document_list):
    all_user_words = user_coll.find({})
    s = []
    for user_word in all_user_words:
        s.append(user_word['word'])
    data = '\n'.join(s)
    with open('./userDict.txt', 'w', encoding='utf-8') as f:
        f.write(data)
    jieba.load_userdict('./userDict.txt')
    tr = WordGroupRank()
    tr.set_stop_words_form_mongo(stop_coll,invalid_coll)

    for idx, doc in enumerate(document_list):
        return tr.text_map(doc,
                           allowPOS=('n', 'nz', 'nr', 'ns', 'nt', 'nw', 'nz', 'v', 'vn', 'f', 's', 'b', 't'))
        if not (idx+1) % 50:
            #print("{} docs processed.".format(idx+1))
            pass


async def fenci_from_mongo(mongo_addr, db, _objectid):
    #print('mongo_addr, db, _objectid',mongo_addr, db, _objectid)
    global coll, user_coll, stop_coll, invalid_coll, count
    # 提供全局数据源
    #mc = MongoClient(mongo_addr,
    #                 unicode_decode_error_handler='ignore')
    mc = client
    db = mc.get_database(db)
    coll = db.get_collection("Articles")
    user_coll = db.get_collection('UserDict')
    invalid_coll = db.get_collection('InvalidDict')
    stop_coll = db.get_collection('StopDict')
    count = coll.count_documents({})
    # 分布式处理的预留，目前只用一个
    worker_count = 1
    idx = 0
    doc_list = text_load_from_mongo(_objectid)
    result = text_map(doc_list)
    #print(result)
    xx = []
    for ele in sorted(result.keys()):
        xx.extend(result[ele])
    result = xx
    #print(result)
    return (result)

if __name__ == '__main__':
    fenci_from_mongo('mongodb://root:root@114.67.113.229:8004', 'KWM-5f9cb931efc5674d30219f08', '5f9cce5398b26c00012db35d')
