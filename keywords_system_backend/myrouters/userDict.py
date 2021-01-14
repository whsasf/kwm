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
from database.db_basic import esRun
from elasticsearch_dsl import Search, Q, Range


router = APIRouter()
dbPrefix = 'KWM'


class UserDictItemInfo(BaseModel):
    #Category body数据模型
    word: str = Query(None, min_length=1, max_length=250)
    operator: str = Query(None, min_length=1, max_length=250)
    #xfrom: str = Query(None, min_length=1, max_length=250)
    source: Optional[str]

class updateUserDictItemInfo(BaseModel):
    # UpdateCategory body数据模型
    word: Optional[str]
    operator: Optional[str]
    #xfrom: str = Query(None, min_length=1, max_length=250)
    source: Optional[str]

class StopDictItemID(BaseModel):
    word: str = Query(None, min_length=1, max_length=250)

@router.post("/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def create_user_words(*, projectName: str = Path(...), currentPage: Optional[int] = 1, pageSize: Optional[int] =10, userDictItemInfo: List[UserDictItemInfo]):
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
        result1 = await createDictItems(dbPrefix + '-' + projectId, 'UserDict', ItemInfos=userDictItemInfo,currentpage=currentPage,pagesize=pageSize)
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


@router.patch("/{projectName}/{_id}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def modify_word(*, projectName: str = Path(...), _id: str, userDictItemInfo: updateUserDictItemInfo):
    """
    修改用户词
    """

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    userDictItemInfo = userDictItemInfo.dict()
    #print('userDictItemInfo',userDictItemInfo)
    # 添加时间戳
    userDictItemInfo['modifiedTime'] = time.strftime(
        "%Y/%m/%d %H:%M:%S", time.localtime())
    # userDictItemInfo['from'] = await getFieldFromCollection(dbPrefix, 'User', 'department', {
    #     'account': userDictItemInfo['operator']})
    if userDictItemInfo['word']:
        userDictItemInfo['word'] = userDictItemInfo['word'].strip()
        userDictItemInfo['length'] = len(userDictItemInfo['word'])
    else:
        userDictItemInfo.pop('word')
    
    if userDictItemInfo['source']:
        userDictItemInfo['source'] = userDictItemInfo['source'].strip()
    else:
        userDictItemInfo.pop('source')

    if userDictItemInfo['operator']:
        userDictItemInfo['operator'] = userDictItemInfo['operator'].strip()
    else:
        userDictItemInfo.pop('operator')

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
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'新用户词名重复，修改失败! 冲突用户词: \'{errMsg}\'')
    except Exception as e:
        # print('其他错误')
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result1)


@router.delete("/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def to_stop_word(*, projectName: str = Path(...), stopDictItems: List[StopDictItemID], currentPage: int = 1, pageSize: int = 10):
    """
    删除用户词
    """

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    deleteDictList = []
    #print('deleteDict',stopDictItems)
    for item in stopDictItems:
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
    #print(stopDictItemID,1111111111111)
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


@router.get("/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def get_words(*, projectName: str = Path(...), sortDict: Optional[str] = '{}', fullMatch:Optional[bool] = False,searchItem: Optional[str] = None, searchItemID: Optional[str] = None,dateRange: Optional[List[str]] = Query(['', '']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query(['']), wordLengthFilter: Optional[List[str]] = Query([''])):
    """
    获取用户词列表
    """

    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    sortDict  = json.loads(sortDict)

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

    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
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

    #8 构造 排序 表达式，如果存在排序的话
    sortMap= {'desc': -1, 'asc': 1}
    if sortDict != {}:
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典 
        for ele in list(sortDict.keys()):
            if sortDict[ele] == 'normal':
                sortDict.pop(ele)
        #print('sortDict',sortDict)
        
        if sortDict != {}:
            # 非空
            sortDicttemp = [(ele,sortMap[sortDict[ele]]) for ele in sortDict]
            sortDict =  sortDicttemp
        else:
            sortDict = []
    
    if not queryDict['$and']:
        del queryDict['$and']
    
    #print('ccc',queryDict,sortDict)
    result = await fetchDictItems(dbPrefix+'-'+projectId, 'UserDict', xfilter=queryDict, xshown=shownDict, xsort=sortDict, currentpage=currentPage, pagesize=pageSize)
    return (result)


@router.get("/es/{projectName}", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def get_words_es(*, projectName: str = Path(...),sortDict: Optional[str] = '{}',highlight: Optional[List[str]] = Query(['']), fullMatch:Optional[bool] = False,showReturn: Optional[List[str]] = Query(['']), searchItem: Optional[str] = None, searchItemID: Optional[str] = None,dateRange: Optional[List[str]] = Query(['', '']), currentPage: int = 1, pageSize: int = 10, operatorFilter: Optional[List[str]] = Query(['']), wordLengthFilter: Optional[List[str]] = Query([''])):
    """
    获取用户词列表 ES 版本
    """

    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    

    # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'KWM-{projectId}.UserDict'.lower()
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
    
    # length
    if wordLengthFilter != ['']:
        wordLengthFilter = unquote(wordLengthFilter[0], 'utf-8').split(',')
        #print('wordLengthFilter',wordLengthFilter)
        # 存在 lengthFilter 查询
        #长度对应字典
        lengthDict = {
        '1':[0,2], 
        '2':[2,4], 
        '3':[4,8], 
        '4':[8,1000],
        }
        ss = ''
        for ele in wordLengthFilter:
            ss = ss + '|' + f'Q("range",**{{"length": {{"gte": {lengthDict[ele][0]},"lt": {lengthDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))


    # 排序设定: 构造 排序 表达式，如果存在排序的话
    sortMap = {'desc': -1, 'asc': 1}
    #print('sortDict',sortDict)
    if sortDict != '{}':
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典 
        sortDict = json.loads(sortDict)
        for ele in list(sortDict.keys()):
            if sortDict[ele] == 'normal':
                sortDict.pop(ele)
        #print('sortDict',sortDict)
        
        if sortDict != {}:
            # 非空
            sortDicttemp = [(ele,sortMap[sortDict[ele]]) for ele in sortDict]
            sortDict =  sortDicttemp
        else:
            sortDict = []
        #print('sortDict',sortDict)
        # 构造 排序命令
        sorts = []
        for ss in sortDict:
            if ss[1] == 1:
                # asc
                sorts.append(ss[0])
            else:
                # desc
                sorts.append('-'+ss[0])
        #print('sorts', sorts)
        s = s.sort(*sorts)
    else:
        #s = s.sort('_id')
        pass

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


@router.get("/{projectName}/isEmpty", dependencies=[Depends(verify_token)],tags=["UserDict"])
async def get_urls(*, projectName: str = Path(...)):
    """
    获取用户词是否为空
    """
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    return await check_if_collection_is_empty(dbPrefix+'-'+projectId, 'UserDict')
