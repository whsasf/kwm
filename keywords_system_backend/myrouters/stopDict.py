from fastapi import APIRouter, HTTPException, Path, Query, Depends
from pydantic import BaseModel
import json
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
import pymongo
from bson import ObjectId
from bson import json_util
from urllib.parse import unquote
from database.db_advanced import findProjectIdFromProjectName, fetchDictItems, createDictItems, updateDictItems, deleteDictItems, ItemExist, check_if_collection_is_empty
from utilities.jwtTools import verify_token, createJWT
from database.db_basic import esRun
from elasticsearch_dsl import Search, Q, Range


router = APIRouter()
dbPrefix = 'KWM'


class StopDictItemInfo(BaseModel):
    # UpdateCategory body数据模型
    word: str
    operator: str
    source: Optional[str]
    exStatus: Optional[str]


class UpdateStatus(BaseModel):
    status: str


@router.post("/", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def create_stop_words(*, currentPage: Optional[int] = 1, pageSize: Optional[int] =10, stopDictItemInfo: List[StopDictItemInfo]):
    """
    新增停止词
    """
    stopDictItemInfo = [urlsItem.dict() for urlsItem in stopDictItemInfo]
    #print('stopDictItemInfo',stopDictItemInfo)
   
    # 处理数据格式
    for item in stopDictItemInfo:
        item['modifiedTime'] = time.strftime(
            "%Y/%m/%d %H:%M:%S", time.localtime())
        # 格式化字符
        item['word'] = item['word'].strip()
        #item['source'] = item['source'] if item['source'] else 'userDicts'

    try:
        result1 = await createDictItems(dbPrefix + '-StopDict', 'StopDict', ItemInfos=stopDictItemInfo, currentpage=currentPage, pagesize=pageSize)
    except pymongo.errors.BulkWriteError as e:
        # key重复错误， 返回重复的项
        # print(e.details['writeErrors'])
        temp = e.details['writeErrors']
        result = [] # 返回重复的项
        for ele in temp:
            result.append(ele['op']['word'])
        #print(result)
        raise HTTPException(status_code=503, detail="停止词已存在,未插入,请修改后重试!" + str(result))
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.patch("/{_id}", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def updateStopWord(*, _id: str, currentPage: Optional[int] = 1, pageSize: Optional[int] =10, stopDictItemInfo: StopDictItemInfo,flag: Optional[str] ='id'):
    """
        修改停止词
    """
    stopDictItemInfo = stopDictItemInfo.dict()
    
    # 添加时间戳
    stopDictItemInfo['modifiedTime'] = time.strftime(
        "%Y/%m/%d %H:%M:%S", time.localtime())
    # 格式化字符
    stopDictItemInfo['word'] = stopDictItemInfo['word'].strip()
    queryDict2 = {}
    if flag != 'word':
        try:
            oid = ObjectId(_id)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            WordID = oid
            queryDict2 = {'_id': WordID}
    else:
        queryDict2 = {'word': _id}
    
    # 删除空的source
    if not stopDictItemInfo['source']:
        stopDictItemInfo.pop('source')

    # exStatus
    if not stopDictItemInfo['exStatus']:
        stopDictItemInfo.pop('exStatus')
    
    #print('stopDictItemInfo',stopDictItemInfo)
    try:
        result1 = await updateDictItems(dbPrefix + '-StopDict', 'StopDict', currentPage=currentPage, pageSize=pageSize, queryDict=queryDict2, setDict={"$set": stopDictItemInfo})
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'停止词冲突: \'{errMsg}\'')
    except Exception as e:
        # 其他错误
        print(e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    return (result1)


@router.delete("/", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def delete_url(*, stopDictItem: List[str]):
    """
    恢复（删除）停止词
    """

    deleteDictList = []
    for word in stopDictItem:
        deleteDict = {'word': word}
        deleteDictList.append(deleteDict)
    #print(deleteDictList)
    result = await deleteDictItems(dbPrefix+'-StopDict', 'StopDict', deleteDictList)
    return (result)


@router.get("/", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def get_stopWords(*,fullMatch:Optional[bool] = False, showReturn: Optional[List[str]] = Query(['']),searchItemID: Optional[str] = None,searchItem: Optional[str] = None, dateRange: Optional[List[str]] = Query(['', '']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query(['']),sourceFilter: Optional[List[str]] = Query([''])):
    """
    获取停止词列表
    """
   
    # 配置 queryDict 和 showDict ，依据 目的的不同
    queryDict = {}
    shownDict = {}
    if operatorFilter != ['']:
        # 存在 categoryFilter 查询
        operatorFilter = unquote(operatorFilter[0], 'utf-8').split(',')
        queryDict['operator'] = {'$in': operatorFilter}
    if sourceFilter != ['']:
        # 存在 sourceFilter 查询
        sourceFilter = unquote(sourceFilter[0], 'utf-8').split(',')
        queryDict['source'] = {'$in': sourceFilter}
   
    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
        #print('dateRange',dateRange)
        if dateRange != ['', '']:
            queryDict['modifiedTime'] = {
                '$gte': dateRange[0], '$lt': dateRange[1]}
    
    if searchItemID:
        try:
            oid = ObjectId(searchItemID)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['_id'] = oid
    else:
        if searchItem:
            # 有关键词查询
            if fullMatch:
                queryDict['word']= searchItem  # 精确匹配
            else:
                queryDict['word'] = {'$regex': searchItem, '$options': 'i'} # 查询包含，且不区分大小写
        #shownDict = {'_id': 1, 'word': 1, 'operator': 1, 'modifiedTime': 1}
    #print('queryDict88:' ,queryDict,shownDict)
    result = await fetchDictItems(dbPrefix + '-StopDict', 'StopDict', xfilter=queryDict,  currentpage=currentPage, pagesize=pageSize)
    #print('result',result)
    return (result)

@router.get("/es", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def get_stopWordsES(*,fullMatch:Optional[bool] = False, highlight: Optional[List[str]] = Query(['']),showReturn: Optional[List[str]] = Query(['']), searchItemID: Optional[str] = None,searchItem: Optional[str] = None, dateRange: Optional[List[str]] = Query(['', '']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query(['']),sourceFilter: Optional[List[str]] = Query([''])):
    """
    获取停止词列表
    """
   
    # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = 'KWM-StopDict.StopDict'.lower()
    #print('_index', _index)
    
    s = Search()


    if operatorFilter != ['']:
        # 存在 categoryFilter 查询
        operatorFilter = unquote(operatorFilter[0], 'utf-8').split(',')
        #queryDict['operator'] = {'$in': operatorFilter}
        operatorFilter = '\"' + '\" \"'.join(operatorFilter) + '\"'
        #print('ccc',operatorFilter)
        q = Q("query_string", query=operatorFilter, fields=['operator'])
        s = s.query(q)

    if sourceFilter != ['']:
        # 存在 sourceFilter 查询
        sourceFilter = unquote(sourceFilter[0], 'utf-8').split(',')
        #queryDict['source'] = {'$in': sourceFilter}
        sourceFilter = '\"' + '\" \"'.join(sourceFilter) + '\"'
        q = Q("query_string", query=sourceFilter, fields=['source'])
        s = s.query(q)
   
    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
        #print('dateRange',dateRange)
        if dateRange != ['', '']:
           #s = s.query('range',**{'timestamp': {'gte': dateRange[0], 'lt': dateRange[1]}}) # 这种也可以，为了统一Q，使用下面的表达式
           r = Q('range',**{'modifiedTime': {'gte': dateRange[0],'lt': dateRange[1]}})
           s = s.query(r)
    
    if searchItem: # single不走 es，所以，此处只有 searchItem 。不会有 searchItemID
        # 有关键词查询
        #queryDict['word'] = {'$regex': searchItem, '$options': 'i'} # 查询包含，且不区分大小写
        q = Q("multi_match", query=f"{searchItem.strip()}", fields=['word'])
        s = s.query(q)
    
    # 返回哪些字段
    if showReturn != ['']:
        showReturn = unquote(showReturn[0], 'utf-8').split(',')
        s = s.source(includes=showReturn)
    else:
        s = s.source(includes=[])
    
    # 高亮哪些字段
    if highlight != ['']:
        highlight = unquote(highlight[0], 'utf-8').split(',')
        #print(highlight)
        s = s.highlight_options(order='score')
        s = s.highlight_options(pre_tags="<strong>")
        s = s.highlight_options(post_tags = "</strong>")
        for ele in highlight: # 每一个逐个添加高亮
            s = s.highlight(ele)

    # 返回页码
    if currentPage == 0 and pageSize == 0:
        # 返回所有数据
        s = s[0:10000] # 这里写死了10000, 如果超过，会报错。最好的解决方法是 用 scan，但是 scan 不会排序。后面再解决
    else:
        start = (currentPage - 1) * pageSize
        end = start + pageSize
        s = s[start:end]


     # 执行
    try:
        response = await esRun(s.to_dict(), _index)  #s.execute(ignore_cache=True)
    except Exception as e:
        print(e)
        return ({'count': 0,'content':[]})
    else:
        totalCount = response.hits.total.value
        temp = response.to_dict()['hits']['hits']
        result = []
        for item in temp:
            tt = {'_id': {'$oid':item['_id']}}
            tt.update(item['_source'])
            if item.get('highlight'):
                tt.update({'highlight':item['highlight']})
            if start >=0 and end > 0:
                tt.update({'id': start+1})
            result.append(tt)
            start = start +1
        #print(result)
        return ({'count': totalCount, 'content': result})



@router.get("/isEmpty", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def get_urls():
    """
    获取停止词列表
    """
    return await check_if_collection_is_empty(dbPrefix + '-StopDict', 'StopDict')
