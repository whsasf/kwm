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
from utilities.jwtTools import verify_token

router = APIRouter()
dbPrefix = 'KWM'


class InvalidDictItemInfo(BaseModel):
    # UpdateCategory body数据模型
    word: str
    operator: str
    source: Optional[str]
    exStatus: Optional[str]


class UpdateStatus(BaseModel):
    status: str


@router.post("/{projectName}",dependencies=[Depends(verify_token)],tags=["InvalidDict"])
async def create_invalid_words(*, projectName: str = Path(...), InvalidDictItemInfo: List[InvalidDictItemInfo]):
    """
    新增无效词
    """

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    invalidDictItemInfo = [urlsItem.dict() for urlsItem in InvalidDictItemInfo]
    
    # 整理数据
    for item in invalidDictItemInfo:
        item['modifiedTime'] = time.strftime(
            "%Y/%m/%d %H:%M:%S", time.localtime())
        # 格式化字符
        item['word'] = item['word'].strip()
    try:
        result1 = await createDictItems(dbPrefix + '-' + projectId, 'InvalidDict', ItemInfos=invalidDictItemInfo)
    except pymongo.errors.BulkWriteError as e:
        # key重复错误， 返回重复的项
        # print(e.details['writeErrors'])
        temp = e.details['writeErrors']
        result = [] # 返回重复的项
        for ele in temp:
            result.append(ele['op']['word'])
        #print(result)
        raise HTTPException(status_code=503, detail="无效词已存在,未插入,请修改后重试!" + str(result))
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.patch("/{projectName}/{_id}",dependencies=[Depends(verify_token)],tags=["InvalidDict"])
async def create_url(*, projectName: str = Path(...), _id: str, InvalidDictItemInfo: InvalidDictItemInfo,flag: Optional[str] ='id'):
    """
    修改无效词
    """
    invalidDictItemInfo = InvalidDictItemInfo.dict()
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    # 检查word是否重复
    item_exist = await ItemExist(dbPrefix+'-'+projectId, 'InvalidDict', {'word': invalidDictItemInfo['word']})
    if item_exist != 'null' and json.loads(item_exist)['_id']['$oid'] != _id:
        return 'item exist'
    # 添加时间戳
    invalidDictItemInfo['modifiedTime'] = time.strftime(
        "%Y/%m/%d %H:%M:%S", time.localtime())

    # 格式化字符
    invalidDictItemInfo['word'] = invalidDictItemInfo['word'].strip()
    queryDict2 ={}
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
    if not invalidDictItemInfo['source']:
        invalidDictItemInfo.pop('source')

    # exStatus
    if not invalidDictItemInfo['exStatus']:
        invalidDictItemInfo.pop('exStatus')

    result1 = await updateDictItems(dbPrefix+'-'+projectId, 'InvalidDict', queryDict=queryDict2, setDict={"$set": invalidDictItemInfo})
    return (result1)


@router.delete("/{projectName}",dependencies=[Depends(verify_token)],tags=["InvalidDict"])
async def delete_url(*, projectName: str = Path(...), stopDictItemID: List[str]):
    """
    恢复（删除）无效词
    """
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    for word in stopDictItemID:
        deleteDict = {'word': word}
        deleteDictList.append(deleteDict)
    result = await deleteDictItems(dbPrefix+'-'+projectId, 'InvalidDict', deleteDictList)
    return (result)


@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["InvalidDict"])
async def get_urls(*, projectName: str = Path(...), fullMatch:Optional[bool] = False, keyword: Optional[str] = None, dataRange: Optional[List[str]] = Query(['','']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query([''])):
    """
    获取无效词列表
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
    if dataRange != ['','']:
        dataRange = unquote(dataRange[0], 'utf-8').split(',')
        if dataRange != ['','']:
            queryDict['modifiedTime'] = {'$gte':dataRange[0],'$lt':dataRange[1]}
    if keyword:
        # 有关键词查询
        if fullMatch:
            queryDict['word'] = keyword # 查询包含，且不区分大小写
        else:
            queryDict['word']= {'$regex': keyword, '$options': 'i'}  # 查询包含，且不区分大小写
        shownDict = {'_id': 1, 'word': 1, 'operator': 1, 'modifiedTime': 1}
    result = await fetchDictItems(dbPrefix+'-'+projectId, 'InvalidDict', xfilter=queryDict, xshown=shownDict,  currentpage=currentPage, pagesize=pageSize)

    return (result)


@router.get("/{projectName}/isEmpty",dependencies=[Depends(verify_token)],tags=["InvalidDict"])
async def get_urls(*, projectName: str = Path(...)):
    """
    获取无效词列表
    """
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    return await check_if_collection_is_empty(dbPrefix+'-'+projectId, 'InvalidDict')