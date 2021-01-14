from fastapi import APIRouter, HTTPException, Path, Depends, Query,BackgroundTasks
from pydantic import BaseModel
import json
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
import pymongo
from bson import ObjectId
from urllib.parse import unquote,quote
from database.db_advanced import fetchExtendedWordsTopic, findProjectIdFromProjectName, addExtendedWords, fetchExtendedWords, deleteExtendedWordsItems, updateExtendedWords, fetchBasicWords,fetchExtendedWordsInherit,jisuanInheritData,add2InheritAggCollection,fetchExtendedWordsInheritAgg,add2TopicAggCollection,fetchExtendedWordsTopicAgg,deleteFromTopicAggCollection
from utilities.jwtTools import verify_token
from database.db_basic import esRun
from elasticsearch_dsl import Search, Q, Range, Index  #connections, Search, Q, Range, Index用来，更新 mapping 设置，可以让word和 topicWord 进行比较


router = APIRouter()
dbPrefix = 'KWM'
topoTreeDeep = 5
esconnection = 'es7_connection'


class NewExtendedWords(BaseModel):
    word: str = Query(None, min_length=1, max_length=250)
    category: List[str]
    mword: str
    baiduIndex: float
    searchCount: int
    bidPrice: float
    baiduIndexM: float
    searchCountM: int
    bidPriceM: float
    baiduComment: str
    usageTag: List[str]
    source: str
    status: str
    topicWord: Optional[str] = None


class Items2Update(BaseModel):
    word: Optional[str] = None
    category: Optional[List[str]] = None
    status: Optional[str] = None
    mword: Optional[str] = None
    usageTag: Optional[List[str]] = None
    baiduIndex: Optional[float] = None
    searchCount: Optional[int] = None
    bidPrice: Optional[float] = None
    baiduIndexM: Optional[float] = None
    searchCountM: Optional[int] = None
    bidPriceM: Optional[float] = None
    baiduComment: Optional[str] = None
    topicWord: Optional[str] = None
    oldTopicWord: Optional[str] = None
    oldMword: Optional[str] = None
    

class topicWords(BaseModel):
    uid: str
    word: str

class DeleteItems(BaseModel):
    uid:str
    topicWord: Optional[str]
    mword: str

class topicWordsUids(BaseModel):
    uid: str
    word: str


@router.post("/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def createExtendedWords(*, projectName: str = Path(...), currentPage: Optional[int] = 1, pageSize: Optional[int] =10, newExtendedWords: List[NewExtendedWords]):
    
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    # 查询Project Name下的所有 目录列表
    #print(projectName, newExtendedWords)
    # projectName 转 projectId
    newExtendedWords = [newExtendedWordsitem.dict()
                        for newExtendedWordsitem in newExtendedWords]
    # 添加一些 计算属性
    for ele in newExtendedWords:
        ele['timestamp'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        ele['Length'] = len(ele['word'])
    #print('newExtendedWords', newExtendedWords)
    
    try:
        result = await addExtendedWords(dbPrefix + '-' + projectId, 'extendedWords', ItemInfos=newExtendedWords, currentPage=currentPage, pagesize=pageSize)
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'重复拓展词: \'{errMsg}\'')
    except pymongo.errors.BulkWriteError as e:
        # key重复错误， 返回重复的项
        # print(e.details['writeErrors'])
        temp = e.details['writeErrors']
        result = [] # 返回重复的项
        for ele in temp:
            result.append(ele['op']['word'])
        #print(result)
        raise HTTPException(status_code=503, detail="以下word重复，未插入,请修改后重试!" + str(result))
    except Exception as e:
        #print('其他错误')
        raise HTTPException(status_code=503, detail=e)
    else:
        return (result)


@router.get("/usageTag/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWords(*, projectName: str = Path(...), ):
    # 查询Project Name下的所有  usagetag
    # projectName 转 projectId
    queryDict = {}
    shownDict = {'_id': 0, 'usageTag': 1}
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    # 现在获取 该项目下 所有 usageTag
    result = await fetchExtendedWords(dbPrefix+'-'+projectId, 'extendedWords', xfilter=queryDict, xshown=shownDict)
    temp = result['content']
    result = set()
    for ele1 in temp:
        if ele1.get('usageTag'):
            for ele2 in ele1['usageTag']:
                result.add(ele2)
    #print({'count': len(result), 'content': list(result)})
    return ({'count': len(result), 'content': list(result)})


@router.get("/InheritSub/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def fetchInheritSub(*, projectName: str = Path(...), word: str, idPrefix: str):
    #print(projectName, word, idPrefix)
    
    # 1- projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    start = []

    async def top2Bottom(word):
        # 1-1 分析每一个 词  有没有 拓展词
        queryDict = {'mword': word}
        shownDict = {'_id': 0, 'word': 1, 'status': 1}
        result = await fetchExtendedWords(dbPrefix+'-'+projectId, 'extendedWords', xfilter=queryDict)
        result = result['content']
        #print('result999', result)
        if len(result) == 0:
            #print('退出')
            # 空，无须往下进行了，退出，
            pass
        else:
            # 先将每一项添加到 start
            start.extend(result)
            # 找到每一份新单词
            temp=[]
            for ele in result:
                # 继续进行
                #print('继续迭代')  
                await top2Bottom(ele['word'])

    await top2Bottom(word)
    #print('start',start)
    # 添加id
    iid = 1
    for ele in start:
        ele['id'] = str(idPrefix)+ '-' +str(iid)
        iid = iid +1
    #print('start',start)
    return (start)


@router.get("/topoTree/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def fetchTopoTree(*, projectName: str = Path(...), word: str, type: str, status: str):
    #print(projectName, word, type, status)
    
    # 1- projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    async def top2Bottom(init, items):
        tempLength = len(items)
        loopReault = [{} for i in range(0, tempLength)]
        for index in range(0, tempLength):
            #loopReault[index]['name'] = '<a href="https://www.baidu.com">' + items[index]['word'] + '</a>'
            loopReault[index]['name'] = items[index]['word']
            if items[index]['status'] == '停止':
                loopReault[index]['label'] = {"backgroundColor": 'red'}
            elif items[index]['status'] == '已添加':
                loopReault[index]['label'] = {"backgroundColor": 'green'}
            else:
                loopReault[index]['label'] = {"backgroundColor": 'blue'}

            if items[index]['word'] == word:
                #  查询的 基词 放大显示
                loopReault[index]['label']['fontSize'] = 40
                loopReault[index]['label']['lineHeight'] = 40
            init.append(loopReault[index])
            # 1-2 分析每一个 词  有没有 拓展词
            queryDict = {'mword': items[index]['word']}
            shownDict = {'_id': 0, 'word': 1, 'status': 1}
            result = await fetchExtendedWords(dbPrefix+'-'+projectId, 'extendedWords', xfilter=queryDict, xshown=shownDict)
            result = result['content']
            #print('loopReault', loopReault)
            #print('result', result)
            if len(result) == 0:
                #print('退出')
                # 空，无须往下进行了，退出，
                pass
            else:
                # 继续进行
                #print('继续')

                init[index]['children'] = []
                loopReault[index]['children'] = []
                await top2Bottom(loopReault[index]['children'], result)

    start = []

    # 2- 查找 拓词树, 深度优先
    if type == 'basic':
        # 对于 基础词 拓词树查询，默认 从该词 向下找 topoTreeDeep = 5

        # 1-1: 先把现有数据，分析添加到数组
        items = [{'word': word, 'status': status}]
        await top2Bottom(start, items)

        # print(start)

    elif type == 'extended':
        # # 对于 拓展词 拓词树查询，默认 从该词 向上找，直到根。然后从该根 按照 top2Bottom往下 遍历

        async def findRoot(word, status):
            # 该函数 用来找到 待查的 word 对应的根词
            queryDict = {'word': word}
            shownDict = {'_id': 0, 'mword': 1, 'status': 1}
            result = await fetchExtendedWords(dbPrefix+'-'+projectId, 'extendedWords', xfilter=queryDict, xshown=shownDict)
            result = result['content']
            # print(result)
            if len(result) == 0:
                # 当前的word 就是mword. 现在需要再查一次 basicWords 表。 如果 该词 在其中存在， 则最终返回该词，否则，返回现在最近的词
                currentWord = word
                currentWordStatus = status

                # 2-2 去母词中找到 根词的 状态
                queryDict = {'word': currentWord}
                shownDict = {'_id': 0, 'status': 1}
                result = await fetchBasicWords(dbPrefix+'-'+projectId, 'basicWords', xfilter=queryDict, xshown=shownDict)
                result = result['content']
                if len(result) > 0:
                    # 存在
                    return ({'rootWord': currentWord, 'rootWordStatus': result[0]['status']})
                else:
                    # 不在 基础表 中 存在
                    return ({'rootWord': currentWord, 'rootWordStatus': currentWordStatus})
            else:
                # 迭代继续
                word = result[0]['mword']
                status = result[0]['status']
                return await findRoot(word, status)

        # 1- 找到 rootWord
        rootWordDict = await findRoot(word, 'status')
        rootWord = rootWordDict['rootWord']
        rootWordStatus = rootWordDict['rootWordStatus']
        #print('==rootWord==', rootWord, rootWordStatus)

        # 3- : 依据 rootWord，和 状态 找到 所有的子词
        items = [{'word': rootWord, 'status': rootWordStatus}]
        await top2Bottom(start, items)
    #print('start',start)
    return (start[0])


@router.get("/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWords(*, projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['', '']), usageTagFilter: Optional[List[str]] = Query(['']), statusFilter: Optional[List[str]] = Query(['']), extendedWordItemId: Optional[str] = '', baiduIndexFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']), searchCountFilter: Optional[List[str]] = Query(['']), bidPriceFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), idPrefix:  Optional[str] = '', wordItem: Optional[str] = 'word', wordPart: Optional[str] = '', sortDict: Optional[str] = '{}', fullMatch: Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] = 10,searchCountMFilter: Optional[List[str]] = Query(['']), bidPriceMFilter: Optional[List[str]] = Query(['']),baiduIndexMFilter: Optional[List[str]] = Query([''])):
    # 查询Project Name下的所有 符合条件的 基础词列表
    #print(projectName, currentPage, pageSize, dateRange, fullMatch, extendedWordItemId,     baiduIndexFilter, lengthFilter, bidPriceFilter, categoryFilter, wordPart, sortDict,searchCountMFilter,bidPriceMFilter,baiduIndexMFilter)

    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案

    # for item in [usageTagFilter,categoryFilter,baiduIndexFilter,lengthFilter,bidPriceFilter,searchCountFilter,statusFilter]:
    #    if item != ['']:
    #        print (item,'1')
    #        item = unquote(item[0], 'utf-8').split(',')

    if categoryFilter != ['']:
        categoryFilter = unquote(categoryFilter[0], 'utf-8').split(',')
        # print(categoryFilter[0])
    if usageTagFilter != ['']:
        usageTagFilter = unquote(usageTagFilter[0], 'utf-8').split(',')
    if baiduIndexFilter != ['']:
        baiduIndexFilter = unquote(baiduIndexFilter[0], 'utf-8').split(',')
    if baiduIndexMFilter != ['']:
        baiduIndexMFilter = unquote(baiduIndexMFilter[0], 'utf-8').split(',')
        # print(type(baiduIndexFilter[0]))
    if lengthFilter != ['']:
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')
    if bidPriceFilter != ['']:
        bidPriceFilter = unquote(bidPriceMilter[0], 'utf-8').split(',')
    if bidPriceMFilter != ['']:
        bidPriceMFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')
    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
    if searchCountFilter != ['']:
        searchCountFilter = unquote(searchCountFilter[0], 'utf-8').split(',')
    if searchCountMFilter != ['']:
        searchCountMFilter = unquote(searchCountMFilter[0], 'utf-8').split(',')
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')

    #print(projectName, currentPage, pageSize, dateRange, fullMatch, statusFilter, extendedWordItemId,
    #      baiduIndexFilter, lengthFilter, bidPriceFilter, categoryFilter, wordPart, sortDict, searchCountFilter,bidPriceMFilter,searchCountMFilter,baiduIndexMFilter)

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    # 初始化 queryDict ，shownDict
    queryDict = {'$and': []}
    shownDict = {}

    # 1- 关键词查询 配置
    if  wordPart and not wordPart.startswith('*') and not wordPart.startswith('?') and not wordPart.startswith('+') and not wordPart.startswith('(') and not wordPart.startswith(')') and not wordPart.endswith('&\\'):
        if len(wordPart) == wordPart.count('\\') and len(wordPart) % 2 == 1:
            wordPart = wordPart + '\\'

        #print('wordItemxxxxx',wordItem)
        if fullMatch:
            queryDict['$and'].append({wordItem: wordPart})
        else:
            queryDict['$and'].append(
                {wordItem: {'$regex': wordPart, '$options': 'i'}})

    # 2- basicWord uid 精准搜索 , 基础词 关键字搜索和 uid 精准搜索 每次搜索 只能选其一
    if extendedWordItemId:
        #  basicWord uid 精准查找
        try:
            oid = ObjectId(extendedWordItemId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['$and'].append({'_id': oid})
    else:
        pass

    # 3- categoryFilter 处理
    if categoryFilter != ['']:
        # 存在 categoryFilter 查询
        queryDict['$and'].append(
            {'category': {'$elemMatch': {'$in': categoryFilter}}})
    else:
        pass

    # 4-1 usageFilter
    if usageTagFilter != ['']:
        # 存在 usageTagFilter
        queryDict['$and'].append(
            {'usageTag': {'$elemMatch': {'$in': usageTagFilter}}})

    # 4- statusFilter 处理
    if statusFilter != ['']:
        # 存在daterange
        queryDict['$and'].append({'status': {'$in': statusFilter}})
    else:
        # 不存在 daterange
        pass

    # 5- dateRange
    if dateRange != ['', '']:
        # 存在 baiduIndexFilter 查询
        queryDict['$and'].append(
            {'timestamp': {'$gte': dateRange[0], '$lt': dateRange[1]}})
    else:
        pass
    # 5-2  searchCountFilter
    # if searchCountFilter !=['']:
    #    queryDict['$and'].append({'searchCount':{'$in':searchCountFilter}})

    # 6- length 筛选
    if lengthFilter != ['']:
        # 存在 lengthFilter 查询
        # 长度对应字典
        lengthDict = {
            '1': [0, 3],
            '2': [3, 5],
            '3': [5, 8],
            '4': [8, 13],
            '5': [13, 18],
            '6': [18, 25]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in lengthFilter:
            tempCampare.append(
                {'Length': {'$gte': lengthDict[ele][0], '$lt': lengthDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 7- bidPriceFilter 筛选
    if bidPriceFilter != ['']:
        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in bidPriceFilter:
            tempCampare.append(
                {'bidPrice': {'$gte': bidPriceDict[ele][0], '$lt': bidPriceDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if bidPriceMFilter != ['']:
        # 存在 bidPriceMFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in bidPriceMFilter:
            tempCampare.append(
                {'bidPriceM': {'$gte': bidPriceDict[ele][0], '$lt': bidPriceDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 8- baiduIndexFilter 筛选
    if baiduIndexFilter != ['']:
        # 存在 baiduIndexFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in baiduIndexFilter:
            tempCampare.append(
                {'baiduIndex': {'$gte': baiduIndexDict[ele][0], '$lt': baiduIndexDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if baiduIndexMFilter != ['']:
        # 存在 baiduIndexMFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in baiduIndexMFilter:
            tempCampare.append(
                {'baiduIndexM': {'$gte': baiduIndexDict[ele][0], '$lt': baiduIndexDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 9- searchCountFilter 筛选
    #print('searchCountFilter',searchCountFilter)
    if searchCountFilter != ['']:
        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in searchCountFilter:
            tempCampare.append(
                {'searchCount': {'$gte': searchCountDict[ele][0], '$lt': searchCountDict[ele][1]}})
        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass
    
    if searchCountMFilter != ['']:
        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in searchCountMFilter:
            tempCampare.append(
                {'searchCountM': {'$gte': searchCountDict[ele][0], '$lt': searchCountDict[ele][1]}})
        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if queryDict['$and'] == []:
        queryDict = {}
    # 8 构造 排序 表达式，如果存在排序的话
    sortMap = {'desc': -1, 'asc': 1}
    if sortDict != '{}':
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典
        sortDict = json.loads(sortDict)
        for ele in list(sortDict.keys()):
            if sortDict[ele] == 'normal':
                sortDict.pop(ele)
        #print('sortDict', sortDict)

        if sortDict != {}:
            # 非空
            sortDicttemp = [(ele, sortMap[sortDict[ele]]) for ele in sortDict]
            sortDict = sortDicttemp
        else:
            sortDict = [('searchCountM', -1)]
    else:
        sortDict = [('searchCountM', -1)]

    #print('queryDict', queryDict, shownDict, sortDict)
    result = await fetchExtendedWords(dbPrefix+'-'+projectId, 'extendedWords',idPrefix = idPrefix, xfilter=queryDict, xshown=shownDict, xsort=sortDict, currentpage=currentPage, pagesize=pageSize)
    return (result)


@router.get("/es/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWords(*, projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['', '']),highlight: Optional[List[str]] = Query(['']),  usageTagFilter: Optional[List[str]] = Query(['']), showReturn: Optional[List[str]] = Query(['']),statusFilter: Optional[List[str]] = Query(['']), extendedWordItemId: Optional[str] = None, baiduIndexFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']), searchCountFilter: Optional[List[str]] = Query(['']), bidPriceFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), idPrefix:  Optional[str] = None, wordItem: Optional[str] = 'word', wordPart: Optional[str] = None, sortDict: Optional[str] = '{}', fullMatch: Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] = 10,searchCountMFilter: Optional[List[str]] = Query(['']), bidPriceMFilter: Optional[List[str]] = Query(['']),baiduIndexMFilter: Optional[List[str]] = Query([''])):
    # 查询Project Name下的所有 符合条件的 基础词列表

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案

    #print(projectName, currentPage, pageSize, dateRange, fullMatch, statusFilter, extendedWordItemId,
    #      baiduIndexFilter, lengthFilter, bidPriceFilter, categoryFilter, wordPart, sortDict, searchCountFilter,bidPriceMFilter,searchCountMFilter,baiduIndexMFilter)
    
    # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.extendedwords'.lower()
    #print('_index', _index)
    s = Search() # 初始化

    #wordPart
    if wordPart:
        q = Q("multi_match", query=f"{wordPart.strip()}", fields=[wordItem])
        s = s.query(q)

    # category
    if categoryFilter != ['']:
        categoryFilter =  unquote(categoryFilter[0], 'utf-8').split(',')
        # print(categoryFilter)
        categoryFilter = '\"' + '\" \"'.join(categoryFilter) + '\"'
        #print('ccc',categoryFilter)
        q = Q("query_string", query=categoryFilter, fields=['category'])
        s = s.query(q)

    # usageTag
    if usageTagFilter != ['']:
        usageTagFilter =  unquote(usageTagFilter[0], 'utf-8').split(',')
        # print(usageTagFilter)
        usageTagFilter = '\"' + '\" \"'.join(usageTagFilter) + '\"'
        #print('ccc',usageTagFilter)
        q = Q("query_string", query=usageTagFilter, fields=['usageTag'])
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

    # baiduIndexFilter
    if baiduIndexFilter != ['']:
        baiduIndexFilter = unquote(baiduIndexFilter[0], 'utf-8').split(',')
        
        # 存在 baiduIndexFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in baiduIndexFilter:
            ss = ss + '|' + f'Q("range",**{{"baiduIndex": {{"gte": {baiduIndexDict[ele][0]},"lt": {baiduIndexDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if baiduIndexMFilter != ['']:
        baiduIndexMFilter = unquote(baiduIndexMFilter[0], 'utf-8').split(',')

        # 存在 baiduIndexMFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in baiduIndexMFilter:
            ss = ss + '|' + f'Q("range",**{{"baiduIndexM": {{"gte": {baiduIndexDict[ele][0]},"lt": {baiduIndexDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if bidPriceFilter != ['']:
        bidPriceFilter = unquote(bidPriceMilter[0], 'utf-8').split(',')

        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in bidPriceFilter:
            ss = ss + '|' + f'Q("range",**{{"bidPrice": {{"gte": {bidPriceDict[ele][0]},"lt": {bidPriceDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if bidPriceMFilter != ['']:
        bidPriceMFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')

        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in bidPriceMFilter:
            ss = ss + '|' + f'Q("range",**{{"bidPriceM": {{"gte": {bidPriceDict[ele][0]},"lt": {bidPriceDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if searchCountFilter != ['']:
        searchCountFilter = unquote(searchCountFilter[0], 'utf-8').split(',')

        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in searchCountFilter:
            ss = ss + '|' + f'Q("range",**{{"searchCount": {{"gte": {searchCountDict[ele][0]},"lt": {searchCountDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))


    if searchCountMFilter != ['']:
        searchCountMFilter = unquote(searchCountMFilter[0], 'utf-8').split(',')

        # 存在 searchCountMFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in searchCountMFilter:
            ss = ss + '|' + f'Q("range",**{{"searchCountM": {{"gte": {searchCountDict[ele][0]},"lt": {searchCountDict[ele][1]}}}}})'
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

    # common setting
    #print('ssss',s.to_dict())

    # 执行
    try:
        response = await esRun(s.to_dict(), _index)  #s.execute(ignore_cache=True)
    except Exception as e:
        print(e)
        return ({'count': 0,'content':[]})
    else:
        #print('response',response)
        totalCount = response.hits.total.value
        temp = response.to_dict()['hits']['hits']
        #print('temp',temp)
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



@router.get("/Inherit/es/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWordsTopic(*, projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']), highlight: Optional[List[str]] =Query(['']),showReturn: Optional[List[str]] = Query(['']),  extendedWordItemId: Optional[str] = None, baiduIndexFilter: Optional[List[str]] = Query(['']),searchCountFilter: Optional[List[str]] = Query(['']), bidPriceFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), wordPart: Optional[str] = None, sortDict: Optional[str] = '{}', fullMatch: Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] = 10,searchCountMFilter: Optional[List[str]] = Query(['']), bidPriceMFilter: Optional[List[str]] = Query(['']),baiduIndexMFilter: Optional[List[str]] = Query([''])):
    # 查询Project Name下的所有 符合条件的 拓展词列表中的  母词 ，母词统计数据位于 inheritAgg 表中

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    #print('projectName',projectName, 'currentPage',currentPage, 'pageSize',pageSize, 'fullMatch',fullMatch, 'extendedWordItemId',extendedWordItemId,
    #      'baiduIndexFilter',baiduIndexFilter, 'bidPriceFilter',bidPriceFilter, 'wordPart',wordPart, 'sortDict',sortDict, 'searchCountFilter',searchCountFilter,'bidPriceMFilter',bidPriceMFilter,'searchCountMFilter',searchCountMFilter,'baiduIndexMFilter',baiduIndexMFilter)

    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.inheritagg'.lower()

    # 首先，更新 index 的 mapping，添加 {'fielddata':True} , 使得 word 和 topicWord字段，可以 整体进行操作
    #xindex = Index(_index, using=esconnection)
    # 给 topicWord 和 word字段 添加 "fielddata": True 属性
    #xindex.put_mapping(using=esconnection, body={"properties": {"word": {"type": "text", "fielddata": True}, "topicWord": {"type": "text", "fielddata": True}}})
    
    # 页码起始
    start = 0
    end = 0
    
    #print('_index', _index)
    s = Search()
    ## 注意此处. 各种尝试了半天，python elasticsearch dsl ，自带的 script_fields 根本 不运行。所以只能根据 从kinina 查询的 原始 jaon数据，反向 构造查询条件。日了狗了简直，，，
    #s= s.from_dict({"query": {"bool": {"filter": {"script": {"script": {"source": "doc['topicWord'].size() > 0 && doc['word'].value == doc['topicWord'].value","lang": "painless"}}}}}}) # 初始化
    ###
    #wordPart

    if extendedWordItemId:
        q = Q("multi_match", query=f"{extendedWordItemId.strip()}", fields=['_id'])
        s = s.query(q)
    else:
        if wordPart:
            q = Q("multi_match", query=f"{wordPart.strip()}", fields=['word'])
            s = s.query(q)

    # baiduIndexFilter
    if baiduIndexFilter != ['']:
        baiduIndexFilter = unquote(baiduIndexFilter[0], 'utf-8').split(',')
        
        # 存在 baiduIndexFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in baiduIndexFilter:
            ss = ss + '|' + f'Q("range",**{{"baiduIndex": {{"gte": {baiduIndexDict[ele][0]},"lt": {baiduIndexDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if baiduIndexMFilter != ['']:
        baiduIndexMFilter = unquote(baiduIndexMFilter[0], 'utf-8').split(',')

        # 存在 baiduIndexMFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in baiduIndexMFilter:
            ss = ss + '|' + f'Q("range",**{{"baiduIndexM": {{"gte": {baiduIndexDict[ele][0]},"lt": {baiduIndexDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if bidPriceFilter != ['']:
        bidPriceFilter = unquote(bidPriceMilter[0], 'utf-8').split(',')

        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in bidPriceFilter:
            ss = ss + '|' + f'Q("range",**{{"bidPrice": {{"gte": {bidPriceDict[ele][0]},"lt": {bidPriceDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if bidPriceMFilter != ['']:
        bidPriceMFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')

        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in bidPriceMFilter:
            ss = ss + '|' + f'Q("range",**{{"bidPriceM": {{"gte": {bidPriceDict[ele][0]},"lt": {bidPriceDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if searchCountFilter != ['']:
        searchCountFilter = unquote(searchCountFilter[0], 'utf-8').split(',')

        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in searchCountFilter:
            ss = ss + '|' + f'Q("range",**{{"searchCount": {{"gte": {searchCountDict[ele][0]},"lt": {searchCountDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))


    if searchCountMFilter != ['']:
        #print('searchCountMFilter',searchCountMFilter)
        searchCountMFilter = unquote(searchCountMFilter[0], 'utf-8').split(',')

        # 存在 searchCountMFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in searchCountMFilter:
            ss = ss + '|' + f'Q("range",**{{"searchCountM": {{"gte": {searchCountDict[ele][0]},"lt": {searchCountDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))
            

    # 排序设定: 构造 排序 表达式，如果存在排序的话
    sortMap = {'desc': -1, 'asc': 1}
    #print('sortDict',sortDict)

    #xx= {'bidPriceM':'topicBidPriceM', 'searchCount':'topicSearchCount', 'baiduIndex': 'topicBaiduIndex', 'baiduIndexM':'topicBaiduIndexM', 'searchCountM':'topicSearchCountM', 'bidPrice':'topicBidPrice'}

    if sortDict != '{}':
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典 
        sortDict = json.loads(sortDict)
        #print('sortDict0',sortDict)
        if len(sortDict) >0:
            for ele in list(sortDict.keys()):
                if sortDict[ele] == 'normal':
                    sortDict.pop(ele)
            #print('sortDict', sortDict)

            if sortDict != {}:
                sortDict2 = {}
                # 非空
                # 将 原始健明 替换为 topic的
                for ele in sortDict:
                    sortDict2[ele] = sortDict[ele]

                sortDict = sortDict2

                sortDicttemp = [(ele,sortMap[sortDict[ele]]) for ele in sortDict]
                sortDict =  sortDicttemp

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
                #sortDict = []
                s = s.sort('-searchCountM')
        else:
            s = s.sort('-searchCountM')
    else:
        s = s.sort('-searchCountM')

    # 返回哪些字段
    #if showReturn != ['']:
    #    showReturn = unquote(showReturn[0], 'utf-8').split(',')
    #    s = s.source(includes=showReturn)
    #else:
    #    s = s.source(includes=[])
    
    # 先写死
    s = s.source(includes=['word','searchCountM','bidPriceM','baiduIndexM','searchCount','bidPrice','baiduIndex'])

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
    #print('ssss',s.to_dict())

    # 执行
    try:
        response = await esRun(s.to_dict(), _index)  #s.execute(ignore_cache=True)
    except Exception as e:
        print(e)
        return ({'count': 0,'content':[]})
    else:
        #print('response',response)
        totalCount = response.hits.total.value
        temp = response.to_dict()['hits']['hits']
        #print('temp',temp)
        result = []
        for item in temp:
            #print('item', item)
            lineData =item['_source']
            tt = {'_id': {'$oid':item['_id']}}
            #tt.update(item['_source'])
            if item.get('highlight'):
                tt.update({'highlight':item['highlight']})
            if start >=0 and end > 0:
                tt.update({'id': start + 1})
            #'topicBidPrice','topicBaiduIndex','topicSearchCount','topicBidPriceM','topicSearchCountM','topicBaiduIndexM'
            tt['bidPrice'] = lineData['bidPrice']
            tt['baiduIndex'] = lineData['baiduIndex']
            tt['searchCount'] = lineData['searchCount']
            tt['baiduIndexM'] = lineData['baiduIndexM']
            tt['bidPriceM'] = lineData['bidPriceM']
            tt['searchCountM'] = lineData['searchCountM']
            tt['word'] = lineData['word']
            tt['children'] = []
            tt['_loading'] = False
            result.append(tt)
            start = start +1
        #print('final',result)
        return ({'count': totalCount, 'content': result})



@router.get("/Topic/es/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWordsTopic(*, projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']), highlight: Optional[List[str]] =Query(['']),showReturn: Optional[List[str]] = Query(['']),  extendedWordItemId: Optional[str] = None, baiduIndexFilter: Optional[List[str]] = Query(['']),searchCountFilter: Optional[List[str]] = Query(['']), bidPriceFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), wordPart: Optional[str] = None, sortDict: Optional[str] = '{}', fullMatch: Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] = 10,searchCountMFilter: Optional[List[str]] = Query(['']), bidPriceMFilter: Optional[List[str]] = Query(['']),baiduIndexMFilter: Optional[List[str]] = Query([''])):
    # 查询Project Name下的所有 符合条件的 主题词 ，主题词统计数据位于 topicAgg 表中

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    #print('projectName',projectName, 'currentPage',currentPage, 'pageSize',pageSize, 'fullMatch',fullMatch, 'extendedWordItemId',extendedWordItemId,
    #      'baiduIndexFilter',baiduIndexFilter, 'bidPriceFilter',bidPriceFilter, 'wordPart',wordPart, 'sortDict',sortDict, 'searchCountFilter',searchCountFilter,'bidPriceMFilter',bidPriceMFilter,'searchCountMFilter',searchCountMFilter,'baiduIndexMFilter',baiduIndexMFilter)

    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.topicagg'.lower()

    # 首先，更新 index 的 mapping，添加 {'fielddata':True} , 使得 word 和 topicWord字段，可以 整体进行操作
    #xindex = Index(_index, using=esconnection)
    # 给 topicWord 和 word字段 添加 "fielddata": True 属性
    #xindex.put_mapping(using=esconnection, body={"properties": {"word": {"type": "text", "fielddata": True}, "topicWord": {"type": "text", "fielddata": True}}})
    
    # 页码起始
    start = 0
    end = 0
    
    #print('_index', _index)
    s = Search()
    ## 注意此处. 各种尝试了半天，python elasticsearch dsl ，自带的 script_fields 根本 不运行。所以只能根据 从kinina 查询的 原始 jaon数据，反向 构造查询条件。日了狗了简直，，，
    #s= s.from_dict({"query": {"bool": {"filter": {"script": {"script": {"source": "doc['topicWord'].size() > 0 && doc['word'].value == doc['topicWord'].value","lang": "painless"}}}}}}) # 初始化
    ###
    #wordPart

    if extendedWordItemId:
        q = Q("multi_match", query=f"{extendedWordItemId.strip()}", fields=['_id'])
        s = s.query(q)
    else:
        if wordPart:
            q = Q("multi_match", query=f"{wordPart.strip()}", fields=['word'])
            s = s.query(q)

    # baiduIndexFilter
    if baiduIndexFilter != ['']:
        baiduIndexFilter = unquote(baiduIndexFilter[0], 'utf-8').split(',')
        
        # 存在 baiduIndexFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in baiduIndexFilter:
            ss = ss + '|' + f'Q("range",**{{"baiduIndex": {{"gte": {baiduIndexDict[ele][0]},"lt": {baiduIndexDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if baiduIndexMFilter != ['']:
        baiduIndexMFilter = unquote(baiduIndexMFilter[0], 'utf-8').split(',')

        # 存在 baiduIndexMFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in baiduIndexMFilter:
            ss = ss + '|' + f'Q("range",**{{"baiduIndexM": {{"gte": {baiduIndexDict[ele][0]},"lt": {baiduIndexDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if bidPriceFilter != ['']:
        bidPriceFilter = unquote(bidPriceMilter[0], 'utf-8').split(',')

        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in bidPriceFilter:
            ss = ss + '|' + f'Q("range",**{{"bidPrice": {{"gte": {bidPriceDict[ele][0]},"lt": {bidPriceDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if bidPriceMFilter != ['']:
        bidPriceMFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')

        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in bidPriceMFilter:
            ss = ss + '|' + f'Q("range",**{{"bidPriceM": {{"gte": {bidPriceDict[ele][0]},"lt": {bidPriceDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))

    if searchCountFilter != ['']:
        searchCountFilter = unquote(searchCountFilter[0], 'utf-8').split(',')

        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in searchCountFilter:
            ss = ss + '|' + f'Q("range",**{{"searchCount": {{"gte": {searchCountDict[ele][0]},"lt": {searchCountDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))


    if searchCountMFilter != ['']:
        #print('searchCountMFilter',searchCountMFilter)
        searchCountMFilter = unquote(searchCountMFilter[0], 'utf-8').split(',')

        # 存在 searchCountMFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }

        ss = ''
        for ele in searchCountMFilter:
            ss = ss + '|' + f'Q("range",**{{"searchCountM": {{"gte": {searchCountDict[ele][0]},"lt": {searchCountDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))
            

    # 排序设定: 构造 排序 表达式，如果存在排序的话
    sortMap = {'desc': -1, 'asc': 1}
    #print('sortDict',sortDict)

    #xx= {'bidPriceM':'topicBidPriceM', 'searchCount':'topicSearchCount', 'baiduIndex': 'topicBaiduIndex', 'baiduIndexM':'topicBaiduIndexM', 'searchCountM':'topicSearchCountM', 'bidPrice':'topicBidPrice'}

    if sortDict != '{}':
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典 
        sortDict = json.loads(sortDict)
        #print('sortDict0',sortDict)
        if len(sortDict) >0:
            for ele in list(sortDict.keys()):
                if sortDict[ele] == 'normal':
                    sortDict.pop(ele)
            #print('sortDict', sortDict)

            if sortDict != {}:
                sortDict2 = {}
                # 非空
                # 将 原始健明 替换为 topic的
                for ele in sortDict:
                    sortDict2[ele] = sortDict[ele]

                sortDict = sortDict2

                sortDicttemp = [(ele,sortMap[sortDict[ele]]) for ele in sortDict]
                sortDict =  sortDicttemp

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
                #sortDict = []
                s = s.sort('-searchCountM')
        else:
            s = s.sort('-searchCountM')
    else:
        s = s.sort('-searchCountM')

    # 返回哪些字段
    #if showReturn != ['']:
    #    showReturn = unquote(showReturn[0], 'utf-8').split(',')
    #    s = s.source(includes=showReturn)
    #else:
    #    s = s.source(includes=[])
    
    # 先写死
    s = s.source(includes=['word','searchCountM','bidPriceM','baiduIndexM','searchCount','bidPrice','baiduIndex'])

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
    #print('ssss',s.to_dict())

    # 执行
    try:
        response = await esRun(s.to_dict(), _index)  #s.execute(ignore_cache=True)
    except Exception as e:
        print(e)
        return ({'count': 0,'content':[]})
    else:
        #print('response',response)
        totalCount = response.hits.total.value
        temp = response.to_dict()['hits']['hits']
        #print('temp',temp)
        result = []
        for item in temp:
            #print('item', item)
            lineData =item['_source']
            tt = {'_id': {'$oid':item['_id']}}
            #tt.update(item['_source'])
            if item.get('highlight'):
                tt.update({'highlight':item['highlight']})
            if start >=0 and end > 0:
                tt.update({'id': start + 1})
            #'topicBidPrice','topicBaiduIndex','topicSearchCount','topicBidPriceM','topicSearchCountM','topicBaiduIndexM'
            tt['bidPrice'] = lineData['bidPrice']
            tt['baiduIndex'] = lineData['baiduIndex']
            tt['searchCount'] = lineData['searchCount']
            tt['baiduIndexM'] = lineData['baiduIndexM']
            tt['bidPriceM'] = lineData['bidPriceM']
            tt['searchCountM'] = lineData['searchCountM']
            tt['word'] = lineData['word']
            tt['children'] = []
            tt['_loading'] = False
            result.append(tt)
            start = start +1
        #print('final',result)
        return ({'count': totalCount, 'content': result})
    

@router.get("/Topic/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWordsInherit(*, projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['', '']),  aggSort: Optional[List[str]] = Query(['']), aggGroupBy: Optional[List[str]] = Query(['']), usageTagFilter: Optional[List[str]] = Query(['']), statusFilter: Optional[List[str]] = Query(['']), extendedWordItemId: Optional[str] = '', baiduIndexFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']), searchCountFilter: Optional[List[str]] = Query(['']), bidPriceFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), wordPart: Optional[str] = '', sortDict: Optional[str] = '{}', fullMatch: Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] = 10,searchCountMFilter: Optional[List[str]] = Query(['']), bidPriceMFilter: Optional[List[str]] = Query(['']),baiduIndexMFilter: Optional[List[str]] = Query([''])):
    # 查询Project Name下的所有 符合条件的 拓展词列表中的  主题词

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    #if aggGroupBy != ['']:
    #    aggGroupBy = unquote(aggGroupBy[0], 'utf-8').split(',')

    sortDict  = json.loads(sortDict)

    if categoryFilter != ['']:
        categoryFilter = unquote(categoryFilter[0], 'utf-8').split(',')
        # print(categoryFilter[0])
    if usageTagFilter != ['']:
        usageTagFilter = unquote(usageTagFilter[0], 'utf-8').split(',')
    if baiduIndexFilter != ['']:
        baiduIndexFilter = unquote(baiduIndexFilter[0], 'utf-8').split(',')
    if baiduIndexMFilter != ['']:
        baiduIndexMFilter = unquote(baiduIndexMFilter[0], 'utf-8').split(',')
        # print(type(baiduIndexFilter[0]))
    if lengthFilter != ['']:
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')
    if bidPriceFilter != ['']:
        bidPriceFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')
    if bidPriceMFilter != ['']:
        bidPriceMFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')
    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
    if searchCountFilter != ['']:
        searchCountFilter = unquote(searchCountFilter[0], 'utf-8').split(',')
    if searchCountMFilter != ['']:
        searchCountMFilter = unquote(searchCountMFilter[0], 'utf-8').split(',')
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')

    #print(projectName, currentPage, pageSize, dateRange, fullMatch, statusFilter, extendedWordItemId,
    #      baiduIndexFilter, lengthFilter, bidPriceFilter, categoryFilter, wordPart, sortDict, searchCountFilter,bidPriceMFilter,searchCountMFilter,baiduIndexMFilter)

    

    # 初始化 queryDict ，shownDict
    queryDict = {'$and': []}
    shownDict = {}

    # 1- 关键词查询 配置
    if wordPart:
        if len(wordPart) == wordPart.count('\\') and len(wordPart) % 2 == 1:
            wordPart = wordPart + '\\'

        if fullMatch:
            queryDict['$and'].append({'word': wordPart})
        else:
            queryDict['$and'].append(
                {'word': {'$regex': wordPart, '$options': 'i'}})

    # 2- extendedWord uid 精准搜索 , 基础词 关键字搜索和 uid 精准搜索 每次搜索 只能选其一
    if extendedWordItemId:
        #  extendedWord uid 精准查找
        try:
            oid = ObjectId(extendedWordItemId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['$and'].append({'_id': oid})
    else:
        pass

    # 3- categoryFilter 处理
    if categoryFilter != ['']:
        # 存在 categoryFilter 查询
        queryDict['$and'].append(
            {'category': {'$elemMatch': {'$in': categoryFilter}}})
    else:
        pass

    # 4-1 usageFilter
    if usageTagFilter != ['']:
        # 存在 usageTagFilter
        queryDict['$and'].append(
            {'usageTag': {'$elemMatch': {'$in': usageTagFilter}}})

    # 4- statusFilter 处理
    if statusFilter != ['']:
        # 存在daterange
        queryDict['$and'].append({'status': {'$in': statusFilter}})
    else:
        # 不存在 daterange
        pass

    # 5- dateRange
    if dateRange != ['', '']:
        # 存在 baiduIndexFilter 查询
        queryDict['$and'].append(
            {'timestamp': {'$gte': dateRange[0], '$lt': dateRange[1]}})
    else:
        pass
    # 5-2  searchCountFilter
    # if searchCountFilter !=['']:
    #    queryDict['$and'].append({'searchCount':{'$in':searchCountFilter}})

    # 6- length 筛选
    if lengthFilter != ['']:
        # 存在 lengthFilter 查询
        # 长度对应字典
        lengthDict = {
            '1': [0, 3],
            '2': [3, 5],
            '3': [5, 8],
            '4': [8, 13],
            '5': [13, 18],
            '6': [18, 25]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in lengthFilter:
            tempCampare.append(
                {'Length': {'$gte': lengthDict[ele][0], '$lt': lengthDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 7- bidPriceFilter 筛选
    if bidPriceFilter != ['']:
        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in bidPriceFilter:
            tempCampare.append(
                {'bidPrice': {'$gte': bidPriceDict[ele][0], '$lt': bidPriceDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if bidPriceMFilter != ['']:
        # 存在 bidPriceMFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in bidPriceMFilter:
            tempCampare.append(
                {'bidPriceM': {'$gte': bidPriceDict[ele][0], '$lt': bidPriceDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 8- baiduIndexFilter 筛选
    if baiduIndexFilter != ['']:
        # 存在 baiduIndexFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in baiduIndexFilter:
            tempCampare.append(
                {'baiduIndex': {'$gte': baiduIndexDict[ele][0], '$lt': baiduIndexDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if baiduIndexMFilter != ['']:
        # 存在 baiduIndexMFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in baiduIndexMFilter:
            tempCampare.append(
                {'baiduIndexM': {'$gte': baiduIndexDict[ele][0], '$lt': baiduIndexDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 9- searchCountFilter 筛选
    #print('searchCountFilter',searchCountFilter)
    if searchCountFilter != ['']:
        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in searchCountFilter:
            tempCampare.append(
                {'searchCount': {'$gte': searchCountDict[ele][0], '$lt': searchCountDict[ele][1]}})
        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass
    
    if searchCountMFilter != ['']:
        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in searchCountMFilter:
            tempCampare.append(
                {'searchCountM': {'$gte': searchCountDict[ele][0], '$lt': searchCountDict[ele][1]}})
        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if queryDict['$and'] == []:
        queryDict = {}
    
    # 8 构造 排序 表达式，如果存在排序的话
    # 构造 sort
    sortMap= {'desc': -1, 'asc': 1}
    if sortDict != {}:
    #if sortDict !=[]:
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典 
        #sortDict = json.loads(sortDict)
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
    else:
        sortDict = [('searchCountM',-1)]

    #print('queryDict', queryDict, shownDict, sortDict)
    
    result = await fetchExtendedWordsInherit(dbPrefix+'-'+projectId, 'topicAgg',xfilter= queryDict,xshown = shownDict,xsort=sortDict,currentpage=currentPage, pagesize = pageSize)
    #print('result666',result)

    for ele in result['content']:
        ele['children'] = []
        ele['_loading'] = False
    return (result)


@router.get("/Inherit/jisuan/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def jisuanExtendedWordsInherit(*, projectName: str = Path(...),background_tasks: BackgroundTasks):
    # 计算 所有母词 统计数据

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # 1- 获得所有的母词 数据
    aggregate = []
    group = {'_id':{}}
    group['_id']['mword'] = '$mword'

    #group['searchCount'] = {'$sum':'$searchCount'} # totalPV, 为了前端 名称统一，改为 searchCount
    #group['bidPrice'] = {'$avg':'$bidPrice'}
    #group['baiduIndex'] = {'$avg':'$baiduIndex'}
    #group['searchCountM'] = {'$sum':'$searchCountM'} # totalPVM, 为了前端 名称统一，改为 searchCountM
    #group['bidPriceM'] = {'$avg':'$bidPriceM'}
    #group['baiduIndexM'] = {'$avg':'$baiduIndexM'}
    aggregate.append({'$match': {}})
    aggregate.append({'$group': group})
    
    mwords = await jisuanInheritData(dbPrefix+'-'+projectId, 'extendedWords',currentPage=0, pageSize = 0, xaggregate = aggregate,)
    #print('所有母词',list(mwords['content']))
    
    # 2- 遍历每个母词，计算 各项统计值，并存入新表
    #for data in mwords['content']:
    #    mword = data['_id']['mword']
        #print(mword)
        # 计算该 母词，下面 所有 词 的  聚合统计数据
    
    # 目前是 批量计算
    mWWords2 = list(set([xx['_id']['mword'] for xx in list(mwords['content'])]))
    background_tasks.add_task(InheritWordsCalculate, mWWords2, projectId)




@router.get("/Inherit/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def getExtendedWordsInherit(*, projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['', '']),  aggSort: Optional[List[str]] = Query(['']), aggGroupBy: Optional[List[str]] = Query(['']), usageTagFilter: Optional[List[str]] = Query(['']), statusFilter: Optional[List[str]] = Query(['']), extendedWordItemId: Optional[str] = '', baiduIndexFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']), searchCountFilter: Optional[List[str]] = Query(['']), bidPriceFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), wordPart: Optional[str] = '', sortDict: Optional[str] = '{}', fullMatch: Optional[bool] = False, currentPage: Optional[int] = 1, pageSize: Optional[int] = 10,searchCountMFilter: Optional[List[str]] = Query(['']), bidPriceMFilter: Optional[List[str]] = Query(['']),baiduIndexMFilter: Optional[List[str]] = Query([''])):
    # 查询Project Name下的所有 符合条件的 拓展词列表中的  母词

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    #if aggGroupBy != ['']:
    #    aggGroupBy = unquote(aggGroupBy[0], 'utf-8').split(',')

    sortDict  = json.loads(sortDict)

    if categoryFilter != ['']:
        categoryFilter = unquote(categoryFilter[0], 'utf-8').split(',')
        # print(categoryFilter[0])
    if usageTagFilter != ['']:
        usageTagFilter = unquote(usageTagFilter[0], 'utf-8').split(',')
    if baiduIndexFilter != ['']:
        baiduIndexFilter = unquote(baiduIndexFilter[0], 'utf-8').split(',')
    if baiduIndexMFilter != ['']:
        baiduIndexMFilter = unquote(baiduIndexMFilter[0], 'utf-8').split(',')
        # print(type(baiduIndexFilter[0]))
    if lengthFilter != ['']:
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')
    if bidPriceFilter != ['']:
        bidPriceFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')
    if bidPriceMFilter != ['']:
        bidPriceMFilter = unquote(bidPriceMFilter[0], 'utf-8').split(',')
    if dateRange != ['', '']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
    if searchCountFilter != ['']:
        searchCountFilter = unquote(searchCountFilter[0], 'utf-8').split(',')
    if searchCountMFilter != ['']:
        searchCountMFilter = unquote(searchCountMFilter[0], 'utf-8').split(',')
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')

    #print(projectName, currentPage, pageSize, dateRange, fullMatch, statusFilter, extendedWordItemId,
    #      baiduIndexFilter, lengthFilter, bidPriceFilter, categoryFilter, wordPart, sortDict, searchCountFilter,bidPriceMFilter,searchCountMFilter,baiduIndexMFilter)

    

    # 初始化 queryDict ，shownDict
    queryDict = {'$and': []}
    shownDict = {}

    # 1- 关键词查询 配置
    if wordPart:
        if len(wordPart) == wordPart.count('\\') and len(wordPart) % 2 == 1:
            wordPart = wordPart + '\\'

        if fullMatch:
            queryDict['$and'].append({'word': wordPart})
        else:
            queryDict['$and'].append(
                {'word': {'$regex': wordPart, '$options': 'i'}})

    # 2- extendedWord uid 精准搜索 , 基础词 关键字搜索和 uid 精准搜索 每次搜索 只能选其一
    if extendedWordItemId:
        #  extendedWord uid 精准查找
        try:
            oid = ObjectId(extendedWordItemId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['$and'].append({'_id': oid})
    else:
        pass

    # 3- categoryFilter 处理
    if categoryFilter != ['']:
        # 存在 categoryFilter 查询
        queryDict['$and'].append(
            {'category': {'$elemMatch': {'$in': categoryFilter}}})
    else:
        pass

    # 4-1 usageFilter
    if usageTagFilter != ['']:
        # 存在 usageTagFilter
        queryDict['$and'].append(
            {'usageTag': {'$elemMatch': {'$in': usageTagFilter}}})

    # 4- statusFilter 处理
    if statusFilter != ['']:
        # 存在daterange
        queryDict['$and'].append({'status': {'$in': statusFilter}})
    else:
        # 不存在 daterange
        pass

    # 5- dateRange
    if dateRange != ['', '']:
        # 存在 baiduIndexFilter 查询
        queryDict['$and'].append(
            {'timestamp': {'$gte': dateRange[0], '$lt': dateRange[1]}})
    else:
        pass
    # 5-2  searchCountFilter
    # if searchCountFilter !=['']:
    #    queryDict['$and'].append({'searchCount':{'$in':searchCountFilter}})

    # 6- length 筛选
    if lengthFilter != ['']:
        # 存在 lengthFilter 查询
        # 长度对应字典
        lengthDict = {
            '1': [0, 3],
            '2': [3, 5],
            '3': [5, 8],
            '4': [8, 13],
            '5': [13, 18],
            '6': [18, 25]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in lengthFilter:
            tempCampare.append(
                {'Length': {'$gte': lengthDict[ele][0], '$lt': lengthDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 7- bidPriceFilter 筛选
    if bidPriceFilter != ['']:
        # 存在 bidPriceFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in bidPriceFilter:
            tempCampare.append(
                {'bidPrice': {'$gte': bidPriceDict[ele][0], '$lt': bidPriceDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if bidPriceMFilter != ['']:
        # 存在 bidPriceMFilter 查询
        # 长度对应字典
        bidPriceDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in bidPriceMFilter:
            tempCampare.append(
                {'bidPriceM': {'$gte': bidPriceDict[ele][0], '$lt': bidPriceDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 8- baiduIndexFilter 筛选
    if baiduIndexFilter != ['']:
        # 存在 baiduIndexFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in baiduIndexFilter:
            tempCampare.append(
                {'baiduIndex': {'$gte': baiduIndexDict[ele][0], '$lt': baiduIndexDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if baiduIndexMFilter != ['']:
        # 存在 baiduIndexMFilter 查询
        # 长度对应字典
        baiduIndexDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in baiduIndexMFilter:
            tempCampare.append(
                {'baiduIndexM': {'$gte': baiduIndexDict[ele][0], '$lt': baiduIndexDict[ele][1]}})

        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass

    # 9- searchCountFilter 筛选
    #print('searchCountFilter',searchCountFilter)
    if searchCountFilter != ['']:
        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in searchCountFilter:
            tempCampare.append(
                {'searchCount': {'$gte': searchCountDict[ele][0], '$lt': searchCountDict[ele][1]}})
        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass
    
    if searchCountMFilter != ['']:
        # 存在 searchCountFilter 查询
        # 长度对应字典
        searchCountDict = {
            '1': [0, 20],
            '2': [20, 50],
            '3': [50, 100],
            '4': [100, 200],
            '5': [200, 500],
            '6': [500, 1000],
            '7': [1000, 2000],
            '8': [2000, 4000],
            '9': [4000, 7000],
            '10': [7000, 10000],
            '11': [10000, 20000],
            '12': [20000, 200000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare = []
        for ele in searchCountMFilter:
            tempCampare.append(
                {'searchCountM': {'$gte': searchCountDict[ele][0], '$lt': searchCountDict[ele][1]}})
        queryDict['$and'].append({'$or': tempCampare})
    else:
        pass


    if queryDict['$and'] == []:
        queryDict = {}
    
    # 8 构造 排序 表达式，如果存在排序的话
    # 构造 sort
    sortMap= {'desc': -1, 'asc': 1}
    if sortDict != {}:
    #if sortDict !=[]:
        # 前端有 排序信息发过来，检查是否有效
        # 装换 sortDict 为 字典 
        #sortDict = json.loads(sortDict)
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
    else:
        sortDict = [('searchCountM',-1)]

    #print('queryDict', queryDict, shownDict, sortDict)
    
    result = await fetchExtendedWordsInherit(dbPrefix+'-'+projectId, 'inheritAgg',xfilter= queryDict,xshown = shownDict,xsort=sortDict,currentpage=currentPage, pagesize = pageSize)
    #print('result666',result)

    for ele in result['content']:
        ele['children'] = []
        ele['_loading'] = False
    return (result)



@router.delete("/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def delete_article(*, projectName: str = Path(...), extendedWordsIDs: List[DeleteItems],background_tasks: BackgroundTasks):

    extendedWordsIDs = [x.dict() for x in extendedWordsIDs]
    #print('extendedWordsIDs',extendedWordsIDs)
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    deleteDictList = []
    topicWordList = set()  # 存放将要 重新计算的  主题词 信息
    mwordList = set() # 存放将要 重新计算的  母词 信息
    for extendedWordsid in extendedWordsIDs:
        try:
            oid = ObjectId(extendedWordsid['uid'])
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        deleteDict = {'_id': oid}
        deleteDictList.append(deleteDict)
        if extendedWordsid['topicWord'] and extendedWordsid['topicWord'] != '':
            topicWordList.add(extendedWordsid['topicWord'])
        if extendedWordsid['mword'] and extendedWordsid['mword'] != '':
            mwordList.add(extendedWordsid['mword'])
    result = await deleteExtendedWordsItems(dbPrefix+'-'+projectId, 'extendedWords', deleteDictList)

    # 如果涉及到主题词，重新计算
    if len(topicWordList) > 0:
        #print('重新计算主题 相关统计数据')
        background_tasks.add_task(topicZuReCalculate, topicWordList, projectId)
    
    # 如果涉及到母词，重新计算
    if len(mwordList) >0:
        #print('重新计算母词 相关统计数据')
        background_tasks.add_task(InheritWordsCalculate, mwordList, projectId)

    return (result)


@router.patch("/{projectName}/{extendedWordItemId}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def update_extendedWords(*, projectName, extendedWordItemId: str = Path(...), currentPage: Optional[int] = 1, pageSize: Optional[int] = 10, items2Update: Optional[Items2Update],flag: Optional[str] ='id',updateType:  Optional[str] ='one' ,background_tasks: BackgroundTasks):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    items2Update = items2Update.dict()
    #print(extendedWordItemId, items2Update)

    # 删除 并保存 里面的 oldTopicWord 和  oldMword 信息
    if 'oldTopicWord' in items2Update:
        oldTopicWord = items2Update.pop('oldTopicWord')
    if 'oldMword' in items2Update:
        oldMword = items2Update.pop('oldMword')


    for ele in list(items2Update.keys()):
        # 所有 更新项，不能为空。否则，会被 置空： 非常恐怖
        #if items2Update[ele] == '' and ele != 'topicWord':
        if items2Update[ele] == None:
            items2Update.pop(ele)

    # 添加新的时间戳 和 长度
    
    #if items2Update.get('status'):
    
    items2Update['timestamp'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    if items2Update.get('word'):
        items2Update['Length'] = len(items2Update.get('word'))

    #print(projectName, extendedWordItemId, oldTopicWord,items2Update, currentPage, pageSize)
    
    # 更新
    if flag != 'id':
        queryDict = {flag: extendedWordItemId}
        setDict = {"$set": items2Update}
        #print('queryDict----',queryDict,'setDict',setDict)
        result = await updateExtendedWords(dbPrefix+'-'+projectId, 'extendedWords', updateType=updateType,queryDict=queryDict, setDict=setDict, currentPage=currentPage, pageSize=pageSize)
        if isinstance(result, str):
            raise HTTPException(status_code=503, detail=result)
        else:

            # 后端更新 主题词相关 统计数据
            topicWords= [] 
            #if items2Update.get('topicWord'):
            if 'topicWord' in items2Update:
                # 前端修改(添加)了 主题词，需要重新计算
                if oldTopicWord:
                    topicWords.append(oldTopicWord)

                if items2Update.get('topicWord') != '':
                    topicWords.append(items2Update.get('topicWord'))
            else:
                # 前端没有修改主题词，但是如果修改了 词语本身的 这6个数量属性，也会 激发 主题词 统计数据，重新计算
                if oldTopicWord:
                    # 主题词存在
                    target = ['baiduIndex','baiduIndex','bidPrice','baiduIndexM','searchCountM','bidPriceM']
                    for ele in target:
                        if items2Update.get(ele):
                            # 如果存在，重新计算，后面几个都不用看
                            topicWords.append(oldTopicWord)
                            break
            if len(topicWords) > 0:
                #print('topicWords',topicWords)
                #print('重新计算主题 相关统计数据')
                background_tasks.add_task(topicZuReCalculate, topicWords, projectId)
            


            # 后端更新 母词 相关 统计数据
            mWords= [] 
            #if items2Update.get('topicWord'):
            if 'mword' in items2Update:
                # 前端修改(添加)了 母词，需要重新计算
                if oldMword:
                    mWords.append(oldMword)

                if items2Update.get('mword') != '':
                        mWords.append(items2Update.get('mword'))
            else:
                # 前端没有修改 母词，但是如果修改了 词语本身的 这6个数量属性，也会 激发 母词词 统计数据，重新计算
                if oldMword:
                    # 母词存在
                    target = ['baiduIndex','baiduIndex','bidPrice','baiduIndexM','searchCountM','bidPriceM']
                    for ele in target:
                        if items2Update.get(ele):
                            # 如果存在，重新计算，后面几个都不用看
                            mWords.append(oldMword)
                            break
            if len(mWords) > 0:
                #print('重新母题 相关统计数据')
                background_tasks.add_task(InheritWordsCalculate, mWords, projectId)


            return (result)
    else:
        try:
            oid = ObjectId(extendedWordItemId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            result = await updateExtendedWords(dbPrefix+'-'+projectId, 'extendedWords', updateType=updateType,queryDict={"_id": oid}, setDict={"$set": items2Update}, currentPage=currentPage, pageSize=pageSize)
            
            if isinstance(result, str):
                raise HTTPException(status_code=503, detail=result)
            else:
                #print('判断是否更新主题词')
                # 后端更新 主题词相关 统计数据
                topicWords= [] 
                #if items2Update.get('topicWord'):
                if 'topicWord' in items2Update:
                    # 前端修改(添加)了 主题词，需要重新计算
                    if oldTopicWord:
                        topicWords.append(oldTopicWord)
                    
                    if items2Update.get('topicWord') != '':
                        topicWords.append(items2Update.get('topicWord'))

                else:
                    # 前端没有修改主题词，但是如果修改了 词语本身的 这6个数量属性，也会 激发 主题词 统计数据，重新计算
                    if oldTopicWord:
                        # 主题词存在
                        target = ['baiduIndex','baiduIndex','bidPrice','baiduIndexM','searchCountM','bidPriceM']
                        for ele in target:
                            if items2Update.get(ele):
                                # 如果存在，重新计算，后面几个都不用看
                                topicWords.append(oldTopicWord)
                                break
                if len(topicWords) > 0:
                    #print('topicWords',topicWords)
                    #print('重新计算主题 相关统计数据')
                    background_tasks.add_task(topicZuReCalculate, topicWords, projectId)

                # 后端更新 母词 相关 统计数据
                mWords= [] 
                #if items2Update.get('mword'):
                if 'mword' in items2Update:
                    # 前端修改(添加)了 母词，需要重新计算
                    if oldMword:
                        mWords.append(oldMword)

                    if items2Update.get('mword') != '':
                            mWords.append(items2Update.get('mword'))
                else:
                    # 前端没有修改 母词，但是如果修改了 词语本身的 这6个数量属性，也会 激发 母词词 统计数据，重新计算
                    if oldMword:
                        # 母词存在
                        target = ['baiduIndex','baiduIndex','bidPrice','baiduIndexM','searchCountM','bidPriceM']
                        for ele in target:
                            if items2Update.get(ele):
                                # 如果存在，重新计算，后面几个都不用看
                                mWords.append(oldMword)
                                break
                if len(mWords) > 0:
                    #print('重新计算母题 相关统计数据')
                    background_tasks.add_task(InheritWordsCalculate, mWords, projectId)

                return (result)


# 删除主题词
@router.delete("/Topic/{projectName}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def updateTopicWord(*, projectName: str = Path(...), currentPage: Optional[int] = 1, pageSize: Optional[int] = 10, uids: List[topicWordsUids],background_tasks: BackgroundTasks):
    
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='项目不存在')

    # uid
    uidList = []
    wordList = []
    uidList2 = []
    for ele in uids:
        ele = ele.dict()
        uidList.append(ele['uid'])
        wordList.append(ele['word'])
        uidList2.append({'word':ele['word']})
    try:
        for uid in uidList:
            oid = ObjectId(uid)
            #uidList2.append({'_id':oid})
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')

    
    # 删除 ,分两步：1 将 extended 表中 该 topicword 清空，2：  从topicAgg 中删除 该topicword 信息
    try:
        for word in wordList:
            queryDict = {'topicWord': word}
            setDict = {'$set': {'topicWord': ''}}
            #print('vvv',queryDict,setDict)
            result1 = await updateExtendedWords(dbPrefix + '-' + projectId, 'extendedWords',updateType="many", queryDict=queryDict, setDict=setDict, currentPage=currentPage, pageSize=pageSize)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail=e)
    else:
        result2 = await deleteFromTopicAggCollection(dbPrefix + '-' + projectId, 'topicAgg', deleteList = uidList2,currentPage=currentPage, pageSize=pageSize)
        return result2


# 添加关键词选项
@router.patch("/{projectName}/Topic/add/{topicWord}", dependencies=[Depends(verify_token)],tags=["extendedWords"])
async def updateTopicWord(*, projectName, topicWord: str = Path(...), currentPage: Optional[int] = 1, pageSize: Optional[int] = 10, uids: List[topicWords],background_tasks: BackgroundTasks):
    
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='项目不存在')

    # 添加新的时间戳
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    #print(uids)
    invalidObjectWord = []
    validObjectItem = []

    for uid in uids:
        temp = uid.dict()
        try:
            oid = ObjectId(temp['uid'])
            validObjectItem.append({'oid':oid,'word':temp['word']})
        except:
            # raise HTTPException(status_code=503, detail='invalid ObjectID')
            invalidObjectWord.append(temp['word'])
    
    # 只要 validObjectItem 不等于空，就设置主题词，最后再返回 无效的 uid 到前端 提示用户
    #print(validObjectItem,invalidObjectWord)
    if len(validObjectItem) == 0:
        # 没有有效数据，直接报错返回
        raise HTTPException(status_code=503, detail='UID 全部无效，请检查!')
    
    # 循环 更新
    setDict = {'topicWord': topicWord,'timestamp':timestamp}
    #print('setDict', setDict)
    result= ''
    
    
    try:
        for item in validObjectItem:
            result = await updateExtendedWords(dbPrefix + '-' + projectId, 'extendedWords', queryDict={"_id": item['oid']}, setDict={"$set": setDict}, currentPage=currentPage, pageSize=pageSize)
    except:
        #print('result',result)
        raise HTTPException(status_code=503, detail=result)
    else:
        # 都成功

        # 后台 进程进行计算 相关任务
        background_tasks.add_task(topicZuReCalculate, [topicWord], projectId)
        if len(invalidObjectWord) == 0:
            # 返回更新后当前页数据
            return (result) # result 正好是最后一次 更新的返回值
        else:
            # 将不合法的uid 返回给前端，其余数据已经更新。 前端收到502 ，会自动请求一次数据
            raise HTTPException(status_code=503, detail='以下单词未找到,请检查:[' + ','.join(invalidObjectWord) + ']')
        
    finally:
        # 执行 后台 主题词相关，计算任务
        pass
        #topicZuReCalculate()

######################### background mission ############

async def topicZuReCalculate(topicWords,pid):
    """
    当 主题词族创建，修改，更新，添加 等 影响到 该族的 以下数据时，重新计算这些数据:
    百度指数，搜索次数，竞价，百度指数-移动，搜索次数-移动，竞价-移动

    topicWords: 为包含 待 重新计算的 主题词族的 名称
    """
    #print('进入后台主题词计算...')
    for topicWord in topicWords:
        aggregate = []
        # match1: 分组前过滤数据
        match1 = {'$and': [{'topicWord': topicWord}]}

        # match2: 分组后过滤数据（输出数据）
        match2 = {'$and':[]}
        group = {}
        skip = 0
        limit = 0

        # 构造 group
        group = {'_id': {'by': topicWord}}

        # 默认，返回这6 项的 聚合: sum(searchCount), avg(bidPrice), avg(baiduIndex),sum(searchCountM), avg(bidPriceM), avg(baiduIndexM)
        group['searchCount'] = {'$sum':'$searchCount'} # totalPV, 为了前端 名称统一，改为 searchCount
        group['bidPrice'] = {'$avg':'$bidPrice'}
        group['baiduIndex'] = {'$avg':'$baiduIndex'}
        group['searchCountM'] = {'$sum':'$searchCountM'} # totalPVM, 为了前端 名称统一，改为 searchCountM
        group['bidPriceM'] = {'$avg':'$bidPriceM'}
        group['baiduIndexM'] = {'$avg':'$baiduIndexM'}

        aggregate.append({'$match': match1})

        if len(group) > 0:
            aggregate.append({'$group': group})

        ##  skip 和 limit 必加，除非想获取全部数据，则不需要加
        #aggregate.append({'$skip': skip})
        #aggregate.append({'$limit': limit})

        #print('aggregatexxx',aggregate)

        result1 = await fetchExtendedWordsTopic(dbPrefix + '-' + pid, 'extendedWords', xaggregate=aggregate,currentPage=0, pageSize = 0)
        #print('result1',result1)
        if result1['count']>0:
            result1 = result1['content'][0]
            result1.pop('_id')
            #print('cccc',result.content[0])
            
            # 将结果写入 topicAgg 表 对应的 主题词 本身
            try:
                #result2 = await updateExtendedWords(dbPrefix + '-' + pid, 'extendedWords', queryDict={'word': topicWord}, setDict={'$set': result1})
                result2 = await add2TopicAggCollection(dbPrefix + '-' + pid, 'topicAgg', xfilter={'word': topicWord}, xset={'$set': result1})
            except Exception as e:
                print(e)
                #print(f'后台重新计算主题词[ {topicWord} ]数据失败')
            else:
                pass
                #print(f'后台重新计算主题词[ {topicWord} ]数据成功')
        else:
            #print('无需从新计算后台主题词统计数据')
            pass


        
async def InheritWordsCalculate(mwords,pid):
    """
    当 母词 词族创建，修改，更新，添加 等 影响到 该族的 以下数据时，重新计算这些数据:
    百度指数，搜索次数，竞价，百度指数-移动，搜索次数-移动，竞价-移动

    mwords: 为包含 待 重新计算的 母词族的 名称
    """
    #print('进入后台 母词计算...')
    for mword in mwords:
        #mword = data['_id']['mword']
        aggregate = []
        # match1: 分组前过滤数据
        match1 = {'$and': [{'mword': mword}]}

        # match2: 分组后过滤数据（输出数据）
        match2 = {'$and':[]}
        group = {}
        skip = 0
        limit = 0

        # 构造 group
        group = {'_id': {'by': mword}}

        # 默认，返回这6 项的 聚合: sum(searchCount), avg(bidPrice), avg(baiduIndex),sum(searchCountM), avg(bidPriceM), avg(baiduIndexM)
        group['searchCount'] = {'$sum':'$searchCount'} # totalPV, 为了前端 名称统一，改为 searchCount
        group['bidPrice'] = {'$avg':'$bidPrice'}
        group['baiduIndex'] = {'$avg':'$baiduIndex'}
        group['searchCountM'] = {'$sum':'$searchCountM'} # totalPVM, 为了前端 名称统一，改为 searchCountM
        group['bidPriceM'] = {'$avg':'$bidPriceM'}
        group['baiduIndexM'] = {'$avg':'$baiduIndexM'}

        aggregate.append({'$match': match1})

        if len(group) > 0:
            aggregate.append({'$group': group})

        ##  skip 和 limit 必加，除非想获取全部数据，则不需要加
        #aggregate.append({'$skip': skip})
        #aggregate.append({'$limit': limit})

        #print('aggregatexxx',aggregate)
        result1 = await fetchExtendedWordsInheritAgg(dbPrefix + '-' + pid, 'extendedWords', xaggregate=aggregate,currentPage=0, pageSize = 0)
        #print('result100000',result1)
        
        # 将数据 写入(更新) 新表 inheritAgg
        if result1['count'] >0:
            tempData = result1['content'][0]
            data2Inset = {'searchCountM': tempData['searchCountM'], 'bidPriceM': tempData['bidPriceM'], 'baiduIndexM': tempData['baiduIndexM'],'searchCount': tempData['searchCount'], 'bidPrice': tempData['bidPrice'], 'baiduIndex': tempData['baiduIndex'] } 

            xfilter = {'word': tempData['_id']['by']}
            xset = {'$set':data2Inset}
            #print(xfilter,xset)
            try:
                result = await add2InheritAggCollection(dbPrefix + '-' + pid,'inheritAgg',xfilter=xfilter,xset=xset)
            except Exception as e:
                #print(f'后台重新计算母词[ {tempData["_id"]["by"]} ]数据失败')
                print('error',e)
            else:
                pass
                #print(f'后台重新计算母词[ {tempData["_id"]["by"]} ]数据成功')
        else:
            #print('无需从新计算后台主题词统计数据')
            pass