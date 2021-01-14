from fastapi import APIRouter, HTTPException, Path, Query, Depends, HTTPException
from pydantic import BaseModel
import json
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
import pymongo
from bson import ObjectId
from bson import json_util
from urllib.parse import unquote
from database.db_advanced import findProjectIdFromProjectName, fetchDictItems, createDictItems, updateDictItems, deleteDictItems, ItemExist, deleteUserDictItems, check_if_collection_is_empty, getFieldFromCollection
from utilities.jwtTools import verify_token

router = APIRouter()
dbPrefix = 'KWM'


class UserDictItemInfo(BaseModel):
    # UpdateCategory body数据模型
    word: str = Query(None, min_length=1, max_length=250)
    operator: str = Query(None, min_length=1, max_length=250)
    xfrom: str = Query(None, min_length=1, max_length=250)
    categories: list = []

class StopDictItemID(BaseModel):
    word: str = Query(None, min_length=1, max_length=250)

@router.post("/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def create_user_words(*, projectName: str = Path(...), userDictItemInfo: List[UserDictItemInfo]):
    """
    新增用户词
    """
    userDictItemInfo = [urlsItem.dict() for urlsItem in userDictItemInfo]
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    # 添加时间戳
    for item in userDictItemInfo:
        item['modifiedTime'] = time.strftime(
            "%Y/%m/%d %H:%M:%S", time.localtime())
        #item['from'] = await getFieldFromCollection(dbPrefix, 'User', 'department', {
        #    'account': item['operator']})
        # item['xfrom'] = item['xfrom'].strip()
        item['word'] = item['word'].strip()
        item['length'] = len(item['word'])
        #item_exist = await ItemExist(dbPrefix+'-'+projectId, 'UserDict', {'word': item['word']})
        #if item_exist != 'null':
        #    return 'item exist'
    # projectName 转 projectId
    try:
        result1 = await createDictItems(dbPrefix + '-' + projectId, 'UserDict', ItemInfos=userDictItemInfo)
    except pymongo.errors.BulkWriteError as e:
        # key重复错误， 返回重复的项
        # print(e.details['writeErrors'])
        temp = e.details['writeErrors']
        result = [] # 返回重复的项
        for ele in temp:
            result.append(ele['op']['word'])
        #print(result)
        raise HTTPException(status_code=503, detail="以下用户词重复，未插入,请修改后重试!" + str(result))
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.put("/{projectName}/{_id}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def modify_word(*, projectName: str = Path(...), _id: str, userDictItemInfo: UserDictItemInfo):
    """
    修改用户词
    """
    userDictItemInfo = userDictItemInfo.dict()
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    # 检查word是否重复
    # item_exist = await ItemExist(dbPrefix+'-'+projectId, 'UserDict', {'word': userDictItemInfo['word']})
    #if item_exist != 'null' and json.loads(item_exist)['_id']['$oid'] != _id:
    #    return 'item exist'
    # 添加时间戳
    userDictItemInfo['modifiedTime'] = time.strftime(
        "%Y/%m/%d %H:%M:%S", time.localtime())
    # userDictItemInfo['from'] = await getFieldFromCollection(dbPrefix, 'User', 'department', {
    #     'account': userDictItemInfo['operator']})
    userDictItemInfo['word'] = userDictItemInfo['word'].strip()
    userDictItemInfo['length'] = len(userDictItemInfo['word'])
    try:
        oid = ObjectId(_id)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        WordID = oid
    try:
        result1 = await updateDictItems(dbPrefix + '-' + projectId, 'UserDict', queryDict={"_id": WordID}, setDict={"$set": userDictItemInfo})
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'新用户词名重复，修改失败! 冲突用户词: \'{errMsg}\'')
    except Exception as e:
        # print('其他错误')
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result1)


@router.delete("/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def to_stop_word(*, projectName: str = Path(...), stopDictItemID: List[StopDictItemID], currentPage: int = 1, pageSize: int = 10):
    """
    删除用户词
    """
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    print('deleteDict',stopDictItemID)
    for item in stopDictItemID:
        deleteDict = {'word': item.dict()['word']}
        deleteDictList.append(deleteDict)
    result = await deleteDictItems(dbPrefix+'-'+projectId, 'UserDict', deleteDictList)
    return (result)


@router.delete("/{projectName}/toStop", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def to_stop_word(*, projectName: str = Path(...), stopDictItemID: List, currentPage: int = 1, pageSize: int = 10):
    """
    用户词转停止词
    """
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    targetDictList = []
    print(stopDictItemID,1111111111111)
    for item in stopDictItemID:
        try:
            oid = ObjectId(item['_id']['$oid'])
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            deleteDict = {'_id': oid}
            deleteDictList.append(deleteDict)
            targetDictList.append({'word': item['word'], 'modifiedTime': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), 'operator': item['operator'], 'source': '用户词','exStatus':''})
    
    result = await deleteUserDictItems(dbPrefix+'-'+projectId, 'UserDict', 'StopDict', currentPage, pageSize, deleteDictList, targetDictList)
    if result == 'error':
        raise HTTPException(status_code=403, detail=result)
    else:
        return (result)


@ router.delete("/{projectName}/toInvalid", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def to_invalid_word(*, projectName: str = Path(...), stopDictItemID: List, currentPage: int = 1, pageSize: int = 10):
    """
    用户词转无效词
    """
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    targetDictList = []
    for item in stopDictItemID:
        try:
            oid = ObjectId(item['_id']['$oid'])
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            deleteDict = {'_id': oid}
            deleteDictList.append(deleteDict)
            targetDictList.append({'word': item['word'], 'modifiedTime': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), 'operator': item['operator'],'source':'用户词','exStatus':''})
    result = await deleteUserDictItems(dbPrefix+'-'+projectId, 'UserDict', 'InvalidDict', currentPage, pageSize, deleteDictList, targetDictList)
    if result == 'error':
        raise HTTPException(status_code=403, detail=result)
    return (result)


@ router.get("/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def get_words(*, projectName: str = Path(...), fullMatch:Optional[bool] = False,keyword: Optional[str] = None, dataRange: Optional[List[str]] = Query(['', '']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query(['']), wordLengthFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query([''])):
    """
    获取用户词列表
    """

    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    # 配置 queryDict 和 showDict ，依据 目的的不同
    queryDict = {}
    shownDict = {}
    queryDict['$and'] = []
    if wordLengthFilter != ['']:
        wordLengthFilter = unquote(wordLengthFilter[0], 'utf-8').split(',')
        lengthDict = {
        '1':[0,2], 
        '2':[2,4], 
        '3':[4,8], 
        '4':[8,1000],
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare= []
        for ele in  wordLengthFilter:
            tempCampare.append({'length':{'$gte':lengthDict[ele][0],'$lt':lengthDict[ele][1]}})
        queryDict['$and'].append({'$or':tempCampare})
    if operatorFilter != ['']:
        # 存在 operatorFilter 查询
        operatorFilter = unquote(operatorFilter[0], 'utf-8').split(',')
        queryDict['operator'] = {'$in': operatorFilter}
    if categoryFilter != ['']:
        # 存在 categoryFilter 查询
        categoryFilter = unquote(categoryFilter[0], 'utf-8').split(',')
        queryDict['$and'].append({'categories':{'$elemMatch':{'$in':categoryFilter}}})
    if dataRange != ['', '']:
        dataRange = unquote(dataRange[0], 'utf-8').split(',')
        if dataRange != ['', '']:
            queryDict['modifiedTime'] = {
                '$gte': dataRange[0], '$lt': dataRange[1]}
    if keyword:
        # 有关键词查询
        #queryDict = {'word': {'$regex': keyword,
        #                      '$options': 'i'}}  # 查询包含，且不区分大小写
        if fullMatch:
            queryDict['$and'].append({'word': keyword})  # 精确匹配
        else:
            queryDict['$and'].append({'word': {'$regex': keyword,'$options': 'i'}})  # 查询包含，且不区分大小写
    print('ccc',queryDict)
    if not queryDict['$and']:
        del queryDict['$and']
    print(queryDict)
    result = await fetchDictItems(dbPrefix+'-'+projectId, 'UserDict', xfilter=queryDict, xshown=shownDict,  currentpage=currentPage, pagesize=pageSize)

    return (result)


@router.get("/{projectName}/isEmpty", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def get_urls(*, projectName: str = Path(...)):
    """
    获取用户词是否为空
    """
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    return await check_if_collection_is_empty(dbPrefix+'-'+projectId, 'UserDict')
