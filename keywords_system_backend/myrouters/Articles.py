from fastapi import APIRouter, HTTPException, Path, Query,Depends,Query
from pydantic import BaseModel, AnyUrl
import json
import re
import pymongo
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from urllib.parse import unquote
from bson import json_util
from urllib.parse import urlparse
from database.db_advanced import findProjectIdFromProjectName, createArticleItems, getArticles,getCategories, deleteArticleItems, updateArticleSplitWords,getArticleBody,addDigInfo,fetchDigInfo,updateDigInfo
from database.db_basic import  update_one
from utilities.fenci import fenci_from_mongo
from utilities.jwtTools import verify_token
from elasticsearch_dsl import Search, Q,Range
from database.db_basic import esRun


router = APIRouter()
dbPrefix = 'KWM'
splitLength = 300
class ArticlesData(BaseModel):
    root: str
    url: str = Query(None,min_length=1,max_length=250)
    title: str
    keywords: List[str]
    desciption: str
    rawContent: str
    body: str
    #Length:int
    splitWords: Optional[List[str]] =[]
    category: List[str]
    #status: str


class NewSplitWords(BaseModel):
    splitWords: List[str]

class NewStatus(BaseModel):
    status: str

class Items2Update(BaseModel):
    splitWords: Optional[List[str]] =''
    status: Optional[str] = ''

class DigInfo(BaseModel):
    operator: str
    taskID: str
    targets: List[str]
    status: str


@router.get("/digMission/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def getDigInfo(*,projectName: str = Path(...)):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
   
    try:
        result1 = await fetchDigInfo(dbPrefix+'-'+projectId,'digMission')
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)

@router.patch("/digMission/{projectName}/{taskID}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def patchDigInfo(*,projectName,taskID: str = Path(...),status: str):
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    toUpdate ={'status': status}
    # 添加结束时间戳
    toUpdate['endTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, toUpdate)
   
    try:
        result1 = await updateDigInfo(dbPrefix+'-'+projectId,'digMission',queryDict={"taskID":taskID},setDict={"$set":toUpdate})
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        # 更新挖取项为 '已挖词'
        # 1- 获取当前 task 包含的 uids
        resultx = await self.getDigInfo(projectName)
        if resultx['count'] > 0:
            for uid in resultx['content'][0]['targets']:
                item = {}
                item['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                item['status'] = '已挖词'
                result1 = await self.update_article(projectName, uid, currentPage=1, pageSize=10, items2Update=item)
        return (result1)


@router.post("/digMission/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def storeDigInfo(*,projectName: str = Path(...),digInfo:DigInfo):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    digInfo = digInfo.dict()
    #print('digInfo',digInfo)
    # 添加时间戳

    digInfo['startTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, digInfo)
   
    try:
        result1 = await addDigInfo(dbPrefix+'-'+projectId,'digMission',ItemInfos = digInfo)
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        # 更改 挖词项 状态 为 '挖词中'
        for uid in digInfo.targets:
            item = {}
            item['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            item['status'] = '挖词中'
            result = await self.update_article(projectName, uid, currentPage=1, pageSize=10, items2Update=item)
        # 返回最后一次的 更新结果
        return (result)


@router.post("/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def create_article(*,projectName: str = Path(...), articlesData:List[ArticlesData]):
    # Article 表中添加 数据 
    #print(projectName)
    articlesData = [articlesItems.dict() for articlesItems in articlesData]
    #print('aiticlesData', articlesData)
    # 添加时间戳,length,status
    for articlesItem in articlesData:
        articlesItem['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        articlesItem['Length'] =  len(articlesItem['body'])
        articlesItem['status'] = '已添加'
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    try:
        result1 = await createArticleItems(dbPrefix+'-'+projectId,'Articles',ItemInfos = articlesData)
    except pymongo.errors.BulkWriteError as e:
        # 出现重复, 如果 是 爬虫写入，则覆盖掉所有重复的项
        # 1- 找到所有重复的项
        temp = e.details['writeErrors']
        results = [] # 返回重复的项
        for ele in temp:
            results.append((ele['op']))
        #print(results)
        # 2- 重新写，这些项，覆盖原有项
        for result in results:
            if urlparse(result['url']).scheme != '':
                # 是从爬虫而来，不是 本地上传
                result.pop('_id')
                #print(result,'nn')
                aa = await update_one(dbPrefix+'-'+projectId,'Articles',{'url':result['url']},{'$set':result})
            else:
                #print('跳过')
                pass # 如果是本地上传的，忽略
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.get("/body/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def fetchArticlBody(*,projectName: str = Path(...),urlItem: str,word: str):
    # 查询 项目数据库，articles 表中数据
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    result = await getArticleBody(dbPrefix + '-' + projectId, 'Articles', xfilter={'url': urlItem}, xshown={'_id': 0, 'body': 1})

    if len(result['content']) >0:
        temp =result['content'][0]['body']
        # print(temp)
        temp = re.split(word,temp)
        #print(temp)
        llength = len(temp)
        if llength >1:
            # 词确实在里面
            # 取每一部分 最多 300个字符
            for i in range(0, llength):
                if i == 0:
                    # 第一个，取 后300个字符
                    temp[i] = temp[i][-splitLength:]
                elif i == llength-1:
                    # 最后一个，取前 300个字符
                    temp[i] = temp[i][0:splitLength]
                else:
                    # 中间的，、暂时获取前300个吧
                    temp[i] = temp[i][0:splitLength]
                    #temp[i] = temp[i][0:int(splitLength/2)] + ' ... ' + temp[i][-int(splitLength/2):]
        else:
            pass # 暂时先什么都不做
        # 2- 将 得到长度满足的 列表，再还原回去
        temp = ('<span style="background: yellow; margin: 0 5px; color: red">' + str(word) + '</span>').join(temp)
        temp = '<div>' + temp + '</div>' 
        result = {'count': llength, 'content': temp}
        return result
    else:
        return ({'count': 0,'content':''})


@router.get("/body/es/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def fetchArticlBody(*,projectName: str = Path(...),urlItem: str,word: str):
    # 查询 项目数据库，articles 表中数据
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.articles'.lower()
    #print('_index', _index)
    
    s = Search()

    q1 = Q("match_phrase", url=f"\"{urlItem}\"") # url 匹配
    q2 = Q('match_phrase', body=f"\"{word}\"") # word 匹配
    s = s.query(q1)
    s = s.query(q2)
    s = s.source(includes=['']) # 不返回输出
    s = s.highlight_options(order='score')
    s = s.highlight_options(pre_tags="<strong style=\"background: yellow;color: red\">")
    s = s.highlight_options(post_tags="</strong>")
    s = s.highlight_options(fragment_size=300) # 
    s = s.highlight('body')
    s = s[0:10000]

    # common setting
    #print(s.to_dict())

    # 执行
    try:
        response = await esRun(s.to_dict(), _index)  #s.execute(ignore_cache=True)
    except Exception as e:
        print(e)
        return ('')
    else:
        #totalCount = response.hits.total.value
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
        return (result)


@router.get("/fenci/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def fenci(*,projectName: str = Path(...),uid:str):
    # 分词
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    if uid:
        try:
            oid = ObjectId(uid)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
    
    #print('fenci', projectId, oid)
    result = await fenci_from_mongo('mongodb://root:root@localhost:27017', f'KWM-{projectId}', oid)
    #print('fenxiresult',result)
    return ({'splitWords': result})




@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def fetchArticles(*,projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']) , urlId:Optional[str]= None, shownItems: Optional[str] = '{}', urlPart:Optional[str] = None, urlFilter: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']), statusFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']),  currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询 特定数据库->articles 表中数据
    
    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # 初始化 queryDict ，shownDict
    queryDict={'$and':[]}
    shownDict = {}
    
    if urlPart and not urlPart.startswith('*') and not urlPart.startswith('?') and not urlPart.startswith('+') and not urlPart.startswith('(') and not urlPart.startswith(')') and not urlPart.endswith('&\\'):
        if len(urlPart) == urlPart.count('\\') and len(urlPart)%2 == 1:
            urlPart = urlPart + '\\'
        queryDict['$and'].append({'url': {'$regex': urlPart, '$options': 'i'}})
    
    if urlId:
        try:
            oid = ObjectId(urlId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['$and'].append({'_id': oid})

    # 配置搜索 条件
    # 1- categoryFilter 处理
    if categoryFilter !=['']:
        # 存在 categoryFilter 查询
        categoryFilter =  unquote(categoryFilter[0], 'utf-8').split(',')
        queryDict['$and'].append({'category':{'$elemMatch':{'$in':categoryFilter}}})
    else:
        pass
    
    # 2- statusFilter 处理
    if statusFilter != ['']:
        # 存在daterange
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')
        queryDict['$and'].append({'status':{'$in':statusFilter}})
    else:
        pass
    
    # 3- dateRange
    #print('dateRangevvvv',dateRange)
    if dateRange != ['','']:
        # 存在 dateRange 查询
        dateRange = unquote(dateRange[0], 'utf-8').split(',')
        if dateRange != ['','']:
            queryDict['$and'].append({'modifiedTime':{'$gte':dateRange[0],'$lt':dateRange[1]}})
    else:
        pass
        
    if lengthFilter != ['']:
        # 存在 lengthFilter 查询
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')
        #长度对应字典
        lengthDict = {
        '1':[0,50], 
        '2':[50,100], 
        '3':[100,300], 
        '4':[300,500],
        '5':[500,1000], 
        '6':[1000,10000]
        }
        # 因为可能有多段数据需要比较，所以先 构造比较的表达式，
        tempCampare= []
        for ele in  lengthFilter:
            tempCampare.append({'Length':{'$gte':lengthDict[ele][0],'$lt':lengthDict[ele][1]}})
        
        queryDict['$and'].append({'$or':tempCampare})
    else:
        pass

    
    if urlFilter != ['']:
        urlFilter = unquote(urlFilter[0], 'utf-8').split(',')
        tempCampare= []
        for ele in urlFilter:
            xx = ''
            if ele  == '1':
                # 有效
                xx = {'url':{'$ne': None}}
            else:
                xx = {'url':{'$eq': None}}
            tempCampare.append(xx)
        queryDict['$and'].append({'$or': tempCampare})
        

    #print('projectName',projectName,'dateRange',dateRange,'lengthFilter','urlFilter',urlFilter,lengthFilter,'statusFilter',statusFilter,'categoryFilter',categoryFilter,'currentPage',currentPage,'pageSize',pageSize)
    
    if queryDict['$and'] == []:
        queryDict = {}
    if shownItems != '{}':
        shownDict = json.loads(shownItems)
    #print ('queryDict,shownDict',queryDict,shownDict)
    result = await getArticles(dbPrefix+'-'+projectId,'Articles',xfilter=queryDict,xshown =shownDict,  currentpage=currentPage,pagesize=pageSize)
    return (result)

@router.get("/es/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def fetchArticles(*,projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']) , urlId:Optional[str]= None, shownItems: Optional[str] = '{}', urlPart:Optional[str] = None, urlFilter: Optional[List[str]] = Query(['']), highlight: Optional[List[str]] = Query(['']), showReturn: Optional[List[str]] = Query(['']), lengthFilter: Optional[List[str]] = Query(['']), statusFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']),  currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询 特定数据库->articles 表中数据
    
    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.articles'.lower()
    #print('_index', _index)
    
    s = Search()

    #urlPart
    #if urlPart:
    #    q = Q("multi_match", query=f"{urlPart.strip()}", fields=['word'])
    #    s = s.query(q)

    if urlPart:  # 通配符 匹配查询
        # 按照url 分隔符进行 分组: '/'
        urlPart = urlPart.replace(':', '')
        urlParts = urlPart.split('/')
        all = []
        all2 = []
        for ele in urlParts:
            all.extend(ele.split('.'))
        for ele in all:
            all2.extend(ele.split('-'))
        q = ''
        for urlPart in all2:
            if urlPart:
                q += f'Q("wildcard", url=f"*{urlPart.strip()}*") &' 
            #q = Q("wildcard", rootUrl=f"*{urlPart.strip()}*") & Q("wildcard", rootUrl=f"*{urlPart.strip()}*")
        q = q.rstrip('&')
        s = s.query(eval(q))


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
            r = Q('range',**{'modifiedTime': {'gte': dateRange[0],'lt': dateRange[1]}})
            s = s.query(r)
    # length
    if lengthFilter != ['']:
        lengthFilter = unquote(lengthFilter[0], 'utf-8').split(',')

        # 存在 lengthFilter 查询
        #长度对应字典
        lengthDict = {
        '1':[0,50], 
        '2':[50,100], 
        '3':[100,300], 
        '4':[300,500],
        '5':[500,1000], 
        '6':[1000,10000]
        }

        ss = ''
        for ele in lengthFilter:
            ss = ss + '|' + f'Q("range",**{{"Length": {{"gte": {lengthDict[ele][0]},"lt": {lengthDict[ele][1]}}}}})'
        #print(ss[1:])
        s = s.query(eval(ss[1:]))
            

    # 排序设定: 构造 排序 表达式，如果存在排序的话
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
        #print('cccc',result)
        return ({'count': totalCount,'content':result})


# @router.get("/{projectName}/Categories",dependencies=[Depends(verify_token)])
# async def fetchCategories(*,projectName: str = Path(...)):
#     # 查询Project Name下的所有 目录列表
#     print(projectName)
#     # projectName 转 projectId
#     projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
#     result = await getCategories(dbPrefix+'-'+projectId,'Categories')
#     #print('cccc',result)
#     return (result)

@router.delete("/{projectName}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def delete_article(*,projectName: str = Path(...),articleIDs: List[str]):
    #print(projectName, articleIDs)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    for articleId in articleIDs:
        try:
            oid = ObjectId(articleId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        deleteDict = {'_id': oid}
        deleteDictList.append(deleteDict)
    result = await deleteArticleItems(dbPrefix+'-'+projectId,'Articles',deleteDictList)
    return (result)

@router.patch("/{projectName}/{articliId}",dependencies=[Depends(verify_token)],tags=["Articles"])
async def update_article(*,projectName,articliId : str = Path(...),currentPage: Optional[int] = 1, pageSize: Optional[int] =10, items2Update: Optional[Items2Update]):
    items2Update = items2Update.dict()
    for ele in list(items2Update.keys()):
        # 所有 更新项，不能为空。否则，会被 置空： 非常恐怖
        if items2Update[ele] == '':
             items2Update.pop(ele)
    
    items2Update['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print('xxx',projectName, articliId,items2Update,currentPage,pageSize)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # 更新
    try:
        oid = ObjectId(articliId)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        try:
            result = await updateArticleSplitWords(dbPrefix+'-'+projectId,'Articles',queryDict={"_id":oid},setDict={"$set": items2Update},currentPage=currentPage,pageSize=pageSize)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
        else:
            return (result)


####### 后台任务 ###########
# 分词

