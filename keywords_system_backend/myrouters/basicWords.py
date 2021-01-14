from fastapi import APIRouter, HTTPException, Path,Depends, Query
from pydantic import BaseModel
import json
from bson import json_util
import pymongo
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from urllib.parse import unquote
from database.db_advanced import findProjectIdFromProjectName, addBasicWords, fetchBasicWords, deleteBacisWordsItems, updateBasicWords,addExpandInfo,updateExpandInfo,fetchExpandInfo
from database.db_basic import esRun
from utilities.jwtTools import verify_token
from elasticsearch_dsl import Search, Q, Range #connections, Search, Q, Range


router = APIRouter()
dbPrefix = 'KWM'

#esconnection = 'es7_connection'
#connections.create_connection(alias=esconnection, hosts=['localhost'], timeout=60)

class NewBasicWords(BaseModel):
    category: Optional[List]
    source: str
    word: str = Query(None, min_length=1, max_length=250)

class Items2Update(BaseModel):
    word: Optional[str] = None
    category: Optional[List[str]] =None
    status: Optional[str] =None

class ExpandInfo(BaseModel):
    operator: str
    taskID: str
    targets: List[str]
    status: str


@router.get("/expandMission/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def getExpandInfo(*,projectName: str = Path(...)):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
   
    try:
        result1 = await fetchExpandInfo(dbPrefix+'-'+projectId,'expandMission')
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.patch("/expandMission/{projectName}/{taskID}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def patchCrawlerInfo(*,projectName,taskID: str = Path(...),status: str):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    toUpdate ={'status': status}
    # 添加结束时间戳
    toUpdate['endTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, toUpdate)
   
    try:
        result1 = await updateExpandInfo(dbPrefix+'-'+projectId,'expandMission',queryDict={"taskID":taskID},setDict={"$set":toUpdate})
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.post("/expandMission/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def storeDigInfo(*,projectName: str = Path(...),expandInfo:ExpandInfo):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    expandInfo = expandInfo.dict()

    #print('expandInfo',expandInfo)
   
    # 添加时间戳
    expandInfo['startTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, expandInfo)
   
    try:
        result1 = await addExpandInfo(dbPrefix+'-'+projectId,'expandMission',ItemInfos = expandInfo)
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)



@router.post("/{projectName}",dependencies=[Depends(verify_token)],tags=["basicWords"])
async def createBasicWords(*,projectName: str = Path(...),newBasicWords: List[NewBasicWords]):

    # projectName 转 projectId
    newBasicWords = [newBasicWordsitem.dict() for newBasicWordsitem in newBasicWords]
    #print(projectName,newBasicWords)
    # 添加一些 计算属性
    for ele in newBasicWords:
        ele['timestamp'] =  time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        ele['Length'] = len(ele['word'])
        ele['status'] = '已添加'  # 默认已添加
        if ele['source'] == '手动添加' or  ele['source'] == '本地文件':
            # 手动输入默认 权重为 0
            ele['weight'] =  0
            # 计算状态 
            # 手动输入状态，有以下结果选项: 无效(已经在无效词典中)，停止（在停止词典中），已添加（在当前表中，但是还没有拓词），(前三个需要 启动API查询)，新词
        
        # 将 source 变成列表， 因为不支持 集合
        ele['source'] = [ele['source'].lower()]
             
    # print(newBasicWords)
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    try:
        result = await addBasicWords(dbPrefix+'-'+projectId,'basicWords',ItemInfos=newBasicWords)
    except pymongo.errors.BulkWriteError as e:
        # 出现重复的key,只把出处（source）添加进 source 列表，其他项丢弃
        # 1- 找到所有重复的项目
        #print('出现重复key')
        temp = e.details['writeErrors']
        #print('temp',temp)
        # 1- 查找 word 的项，对应的 出处
        duplicatedItems = []
        for ele in temp:
            #print('ele: ',ele)
            queryDict= {'word': ele['op']['word']}
            shownDict = {'_id':0, 'source':1}
            result = await fetchBasicWords(dbPrefix+'-'+projectId,'basicWords',xfilter= queryDict,xshown = shownDict)
            if result['count'] == 1:
                # 存在,修改并更新
                tempSource = result['content'][0]['source']
                # 如果 来源，已经存在，那么返回重复，否则，将新来源，添加进 来源列表
                if ele['op']['source'][0].lower() in tempSource:
                    # 已经存在，直接返回
                    #raise HTTPException(status_code=503, detail=f'以下基础词出现重复,未添加: [{ele["op"]["word"]}]')

                    duplicatedItems.append(ele["op"]["word"])
                else:
                    # 新的 来源，则插入
                    tempSource.append(ele['op']['source'][0])
                    tempSource = list(set(tempSource))
                    #print(tempSource)
                    # 2- 覆盖之前的词, 在basicWords中
                    try:
                        timestamp =  time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                        result = await updateBasicWords(dbPrefix+'-'+projectId,'basicWords',queryDict={"word":ele['op']['word']},setDict={"$set": {'source':tempSource,'timestamp': timestamp}})
                    except Exception as e:
                        #print(e)
                        continue
            else:
                # 不存在，跳过. 应该是不存在的情况
                continue

        if duplicatedItems != []:
            # 存在重复数据(来源也重复)
            raise HTTPException(status_code=503, detail='以下基础词出现重复,未添加: ' + str(duplicatedItems))
        # 返回最终数据
        result = await fetchBasicWords(dbPrefix+'-'+projectId,'basicWords')
        return (result)

    except Exception as e:
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result)


@router.get("/es/{projectName}",dependencies=[Depends(verify_token)],tags=["basicWords"])
async def getBasicWords(*,projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['', '']) , basicWordItemId: Optional[str] = None, highlight: Optional[List[str]] = Query(['']), showReturn: Optional[List[str]] = Query(['']), statusFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']),weightFilter: Optional[List[str]] = Query(['']),categoryFilter: Optional[List[str]] = Query(['']), wordPart:Optional[str] = None ,sortDict:Optional[str] = '{}', fullMatch:Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询Project Name下的所有 符合条件的 基础词列表,使用es
    # 要查询的 es索引，类似于  mongodb中的数据库
    # projectName 转 projectId
    #print(projectName,currentPage,pageSize,dateRange,fullMatch,basicWordItemId,statusFilter,lengthFilter,weightFilter,categoryFilter,wordPart,sortDict)

    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    

    # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.basicwords'.lower()
    #print('_index', _index)
    
    s = Search()

    #wordPart
    if wordPart:
        q = Q("multi_match", query=f"{wordPart.strip()}", fields=['word'])
        s = s.query(q)

    # category
    if categoryFilter != ['']:
        categoryFilter =  unquote(categoryFilter[0], 'utf-8').split(',')
        # print(categoryFilter)
        categoryFilter = '\"' + '\" \"'.join(categoryFilter) + '\"'
        #print('ccc',categoryFilter)
        q = Q("query_string", query=categoryFilter, fields=['category'])
        s = s.query(q)
    
    #statusfilter 
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')
        statusFilter = '\"' + '\" \"'.join(statusFilter) + '\"'
        #print('ccc',statusFilter)
        q = Q("query_string", query=f"{statusFilter}", fields=['status'])
        s = s.query(q)

    # dateRange
    # 此处 因为  dateRange 的格式问题 会有一些问题，所以先 用两次判断 解决
    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
        #print('dateRange', dateRange)
        if dateRange != ['', '']:
            #s = s.query('range',**{'timestamp': {'gte': dateRange[0], 'lt': dateRange[1]}}) # 这种也可以，为了统一Q，使用下面的表达式
            r = Q('range',**{'timestamp': {'gte': dateRange[0],'lt': dateRange[1]}})
            s = s.query(r)
    # length
    if lengthFilter != ['']:
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')

        # 存在 lengthFilter 查询
        #长度对应字典
        lengthDict = {
        '1':[0,3], 
        '2':[3,5], 
        '3':[5,8], 
        '4':[8,13],
        '5':[13,18], 
        '6':[18,25]
        }

        ss = ''
        for ele in lengthFilter:
            ss = ss + '|' + f'Q("range",**{{"Length": {{"gte": {lengthDict[ele][0]},"lt": {lengthDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    # 权重配置
    if weightFilter != ['']:
        weightFilter = unquote(weightFilter[0], 'utf-8').split(',')
        #权重对应字典
        weightDict = {
        '1':[0,0.3], 
        '2':[0.3,0.5], 
        '3':[0.5,1], 
        '4':[1,5],
        '5':[5,10], 
        '6':[10,20],
        '7':[20,50]
        }

        ss = ''
        for ele in weightFilter:
            ss = ss + '|' + f'Q("range",**{{"weight": {{"gte": {weightDict[ele][0]},"lt": {weightDict[ele][1]}}}}})'
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
        s = s.sort('_id')

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


    # common setting
    #print(s.to_dict())

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
        return ({'count': totalCount,'content':result})


@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["basicWords"])
async def getBasicWords(*,projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']) , basicWordItemId: Optional[str] = None, statusFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']),weightFilter: Optional[List[str]] = Query(['']),categoryFilter: Optional[List[str]] = Query(['']), wordPart:Optional[str] = None ,sortDict:Optional[str] = [], fullMatch:Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询Project Name下的所有 符合条件的 基础词列表
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    #print('projectIdcc',projectId)
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    #print(projectName,currentPage,pageSize,dateRange,fullMatch,basicWordItemId,statusFilter,lengthFilter,weightFilter,categoryFilter,wordPart,sortDict)

    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案
    #print('categoryFilter',categoryFilter)
    if categoryFilter != ['']:
        categoryFilter =  unquote(categoryFilter[0], 'utf-8').split(',')
        #print(categoryFilter[0])
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')
        #print(type(statusFilter[0]))
    if lengthFilter != ['']:
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')
    if weightFilter != ['']:
        weightFilter = unquote(weightFilter[0], 'utf-8').split(',')
    if dateRange != ['','']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
    
    #print(projectName,currentPage,pageSize,dateRange,fullMatch,basicWordItemId,statusFilter,lengthFilter,weightFilter,categoryFilter,wordPart,sortDict)

    
    # 初始化 queryDict ，shownDict
    queryDict={'$and':[]}
    shownDict={}

    # 1- 关键词查询 配置
    if wordPart:
        if len(wordPart) == wordPart.count('\\') and len(wordPart)%2 == 1:
            wordPart = wordPart + '\\'

        if fullMatch:
            queryDict['$and'].append({'word':wordPart})
        else:
            queryDict['$and'].append({'word':{'$regex':wordPart,'$options':'i'}})

    # 2- basicWord uid 精准搜索 , 基础词 关键字搜索和 uid 精准搜索 每次搜索 只能选其一
    if basicWordItemId:
        #  basicWord uid 精准查找
        try:
            oid = ObjectId(basicWordItemId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['$and'].append({'_id': oid})
    else:
        pass

    # 3- categoryFilter 处理
    if categoryFilter !=['']:
        # 存在 categoryFilter 查询
         queryDict['$and'].append({'category':{'$elemMatch':{'$in':categoryFilter}}})
    else:
        pass
    
    # 4- statusFilter 处理
    if statusFilter != ['']:
        # 存在daterange
        queryDict['$and'].append({'status':{'$in':statusFilter}})
    else:
        # 不存在 daterange
        pass

    # 5- dateRange
    if dateRange != ['','']:
        # 存在 statusFilter 查询
        queryDict['$and'].append({'timestamp': {'$gte':dateRange[0],'$lt':dateRange[1]}})
    else:
        pass

    #6- length 筛选
    if lengthFilter != ['']:
        # 存在 lengthFilter 查询
        #长度对应字典
        lengthDict = {
        '1':[0,3], 
        '2':[3,5], 
        '3':[5,8], 
        '4':[8,13],
        '5':[13,18], 
        '6':[18,25]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare= []
        for ele in  lengthFilter:
            tempCampare.append({'Length':{'$gte':lengthDict[ele][0],'$lt':lengthDict[ele][1]}})
        
        queryDict['$and'].append({'$or':tempCampare})
    else:
        pass

    #7- weight 筛选
    if weightFilter != ['']:
        # 存在 weightFilter 查询
        #权重对应字典
        weightDict = {
        '1':[0,0.3], 
        '2':[0.3,0.5], 
        '3':[0.5,1], 
        '4':[1,5],
        '5':[5,10], 
        '6':[10,20],
        '7':[20,50]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare= []
        for ele in  weightFilter:
            tempCampare.append({'weight':{'$gte':weightDict[ele][0],'$lt':weightDict[ele][1]}})
        
        queryDict['$and'].append({'$or':tempCampare})
    else:
        pass

    if queryDict['$and'] == []:
        queryDict= {}
    #8 构造 排序 表达式，如果存在排序的话
    sortMap= {'desc': -1, 'asc': 1}
    if sortDict !=[]:
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
    
    #print('queryDict',queryDict,shownDict,sortDict)
    result = await fetchBasicWords(dbPrefix+'-'+projectId,'basicWords',xfilter= queryDict,xshown = shownDict,xsort=sortDict,currentpage=currentPage,pagesize=pageSize)
    return (result)


@router.delete("/{projectName}",dependencies=[Depends(verify_token)],tags=["basicWords"])
async def delete_article(*,projectName: str = Path(...),basicWordsIDs: List[str]):
    #print(projectName, basicWordsIDs)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    for basicWordsid in basicWordsIDs:
        try:
            oid = ObjectId(basicWordsid)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            deleteDict = {'_id': oid}
            deleteDictList.append(deleteDict)
    result = await deleteBacisWordsItems(dbPrefix+'-'+projectId,'basicWords',deleteDictList)
    return (result)


@router.patch("/{projectName}/{basicWordItemId}",dependencies=[Depends(verify_token)],tags=["basicWords"])
async def update_basicWords(*,projectName,basicWordItemId : str = Path(...),currentPage: Optional[int] = 1, pageSize: Optional[int] =10, items2Update: Optional[Items2Update],flag: Optional[str] ='id'):
    items2Update = items2Update.dict()
    
    for ele in list(items2Update.keys()):
        # 所有 更新项，不能为空。否则，会被 置空： 非常恐怖
        if items2Update[ele] == None:
             items2Update.pop(ele)
    #print('hahhah',basicWordItemId,items2Update)
    
    # 添加新的时间戳 和 长度
    items2Update['timestamp'] =  time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    if items2Update.get('word'):
        items2Update['Length'] = len(items2Update.get('word'))

    #print(projectName, basicWordItemId,items2Update,currentPage,pageSize)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    # 更新
    if flag == 'word':
        # 按照word 查找，而不是 id
        result = await updateBasicWords(dbPrefix+'-'+projectId,'basicWords',queryDict={"word":basicWordItemId},setDict={"$set": items2Update},currentPage=currentPage,pageSize=pageSize)
        if isinstance(result, str):
            raise HTTPException(status_code=503, detail=result)
        else:
            return (result)

    else:
        try:
            oid = ObjectId(basicWordItemId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            result = await updateBasicWords(dbPrefix+'-'+projectId,'basicWords',queryDict={"_id":oid},setDict={"$set": items2Update},currentPage=currentPage,pageSize=pageSize)
            if isinstance(result, str):
                raise HTTPException(status_code=503, detail=result)
            else:
                return (result)