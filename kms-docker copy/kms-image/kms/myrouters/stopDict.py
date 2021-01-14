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


@router.post("/{projectName}", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def create_stop_words(*, projectName: str = Path(...), currentPage: Optional[int] = 1, pageSize: Optional[int] =10, stopDictItemInfo: List[StopDictItemInfo]):
    """
    新增停止词
    """
    stopDictItemInfo = [urlsItem.dict() for urlsItem in stopDictItemInfo]
    print('stopDictItemInfo',stopDictItemInfo)
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    # 处理数据格式
    for item in stopDictItemInfo:
        item['modifiedTime'] = time.strftime(
            "%Y/%m/%d %H:%M:%S", time.localtime())
        # 格式化字符
        item['word'] = item['word'].strip()
        #item['source'] = item['source'] if item['source'] else 'userDicts'

    try:
        result1 = await createDictItems(dbPrefix + '-' + projectId, 'StopDict', ItemInfos=stopDictItemInfo, currentpage=currentPage, pagesize=pageSize)
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


@router.patch("/{projectName}/{_id}", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def updateStopWord(*, projectName: str = Path(...), _id: str, currentPage: Optional[int] = 1, pageSize: Optional[int] =10, stopDictItemInfo: StopDictItemInfo,flag: Optional[str] ='id'):
    """
        修改停止词
    """
    stopDictItemInfo = stopDictItemInfo.dict()
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
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
    
    print('stopDictItemInfo',stopDictItemInfo)
    try:
        result1 = await updateDictItems(dbPrefix + '-' + projectId, 'StopDict', currentPage=currentPage, pageSize=pageSize, queryDict=queryDict2, setDict={"$set": stopDictItemInfo})
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'停止词冲突: \'{errMsg}\'')
    except Exception as e:
        # 其他错误
        print(e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    return (result1)


@router.delete("/{projectName}", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def delete_url(*, projectName: str = Path(...), stopDictItem: List[str]):
    """
    恢复（删除）停止词
    """
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    for word in stopDictItem:
        deleteDict = {'word': word}
        deleteDictList.append(deleteDict)
    #print(deleteDictList)
    result = await deleteDictItems(dbPrefix+'-'+projectId, 'StopDict', deleteDictList)
    return (result)


@router.get("/{projectName}", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def get_urls(*, projectName: str = Path(...), fullMatch:Optional[bool] = False, keyword: Optional[str] = None, dataRange: Optional[List[str]] = Query(['', '']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query(['']),sourceFilter: Optional[List[str]] = Query([''])):
    """
    获取停止词列表
    """
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
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
    
    if dataRange != ['', '']:
        dataRange = unquote(dataRange[0], 'utf-8').split(',')
        if dataRange != ['', '']:
            queryDict['modifiedTime'] = {
                '$gte': dataRange[0], '$lt': dataRange[1]}
    if keyword:
        # 有关键词查询
        if fullMatch:
            queryDict['word']= keyword  # 精确匹配
        else:
            queryDict['word'] = {'$regex': keyword, '$options': 'i'} # 查询包含，且不区分大小写
        shownDict = {'_id': 1, 'word': 1, 'operator': 1, 'modifiedTime': 1}
    print('queryDict:' ,queryDict)
    result = await fetchDictItems(dbPrefix+'-'+projectId, 'StopDict', xfilter=queryDict, xshown=shownDict,  currentpage=currentPage, pagesize=pageSize)

    return (result)


@router.get("/{projectName}/isEmpty", dependencies=[Depends(verify_token)],tags=["StopDict"])
async def get_urls(*, projectName: str = Path(...)):
    """
    获取停止词列表
    """
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    return await check_if_collection_is_empty(dbPrefix+'-'+projectId, 'StopDict')
