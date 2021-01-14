from fastapi import APIRouter, HTTPException, Path, Query,Depends
from pydantic import BaseModel, conlist
import json
import pymongo
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from urllib.parse import unquote
from bson import json_util
from database.db_advanced import createUrlItems, findProjectIdFromProjectName,fetchUrlItems,updateUrlItems, deleteUrlItems, getCategories,addCrawlerInfo,fetchCrawlerInfo,updateCrawlerInfo
from utilities.jwtTools import verify_token
from database.db_basic import esRun
from elasticsearch_dsl import Search, Q, Range#,Index #connections, Search, Q, Range


from elasticsearch_dsl import connections, Search



router = APIRouter()
dbPrefix = 'KWM'
esconnection = 'es7_connection'

connections.create_connection(hosts=['localhost'], timeout=60)

class UrlPath(BaseModel):
    #path: str = Query(None, min_length=7, max_length=250,regex="^https?://")
    #type: str = Query(None, min_length=2, max_length=250,regex="^包含$|^regex$")
    path: Optional[str] = ""
    type: Optional[str] = ""

class UrlsItemInfo(BaseModel):
    # UpdateCategory body数据模型
    rootUrl: str = Query(None, min_length=7, max_length=250,regex="^https?://")
    #category: List[str] = Query([],min_length=1)
    category: conlist(str, min_items = 1)
    status: str
    urlExcludePath: Optional[List[UrlPath]] = None
    urlIncludePath: Optional[List[UrlPath]] = None

class UpdateStatus(BaseModel):
    status: str
    types: Optional[str] = 'id'

#@router.patch("/{projectName}/{categoryId}")
#async def update_category(*,projectName,categoryId: str = Path(...), updateCategoryInfo: UpdateCategoryInfo):
#    # 修改特定数据库中的分类
#    # print(projectName,categoryId,updateCategoryInfo.dict())
#    
#    queryDict = {'_id': ObjectId(categoryId)}
#    setDict = updateCategoryInfo.dict()
#    setDict = {"$set": setDict }
#    result = await updateCategory(dbPrefix+'-'+projectName,'Categories',queryDict,setDict)
#    return (result)
#
#@router.delete("/{projectId}/{categoryId}")
#async def delete_category(*,projectId,categoryId: str = Path(...)):
#    # 删除特定项目中的特定目录: 
#    # print(projectName,categoryId)
#    queryDict = {'_id': ObjectId(categoryId)}
#    result = await deleteCategory(dbPrefix+'-'+projectId,'Categories',queryDict)
#    return (result)

class CrawlerInfo(BaseModel):
    operator: str
    taskID: str
    targets: List[str]
    status: str


@router.get("/crawlerMission/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def getCrawlerInfo(*,projectName: str = Path(...)):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
   
    try:
        result1 = await fetchCrawlerInfo(dbPrefix+'-'+projectId,'crawlerMission')
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.patch("/crawlerMission/{projectName}/{taskID}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def patchCrawlerInfo(*,projectName,taskID: str = Path(...),status: str):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    #print('crawlerInfo',crawlerInfo)
    toUpdate ={'status': status}
    # 添加结束时间戳
    toUpdate['endTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, toUpdate)
   
    try:
        result1 = await updateCrawlerInfo(dbPrefix+'-'+projectId,'crawlerMission',queryDict={"taskID":taskID},setDict={"$set":toUpdate})
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        # 将状态 改为 成功
        # 1- 获取 当前任务，对应的 url 列表
        resultx= getCrawlerInfo(projectName)
        # 2- 将每一个列表项 状态改为 成功
        allP = {}
        if resultx['count'] >0:
            for url in resultx['content'][0]['targets']:
                allP['queryBy'] = 'url'
                allP['queryValue'] = url
                allP['status'] = '成功'

            result1 = await update_Url_basd_url(projectName, allP)
        
        return (result1)


@router.post("/crawlerMission/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def storeCrawlerInfo(*,projectName: str = Path(...),crawlerInfo:CrawlerInfo):
    
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    crawlerInfo = crawlerInfo.dict()
    #print('crawlerInfo',crawlerInfo)
    # 添加时间戳
    crawlerInfo['startTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, crawlerInfo)
   
    try:
        result1 = await addCrawlerInfo(dbPrefix+'-'+projectId,'crawlerMission',ItemInfos = crawlerInfo)
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        # 将状态 改为爬取中
        allP={}
        for url in crawlerInfo.targets:
            allP['queryBy'] = 'url'
            allP['queryValue'] = url
            allP['status'] = '爬取中'

        result = await update_Url_basd_url(projectName,allP)
        return (result1)


@router.post("/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def create_url(*,projectName: str = Path(...),currentPage: int = 1, pageSize: int =10, urlsItemInfos:List[UrlsItemInfo]):
    # Url表中添加 数据 
    #print(projectName, urlsItemInfos)
    urlsItemInfos = [urlsItem.dict() for urlsItem in urlsItemInfos]
    # 添加时间戳
    for urlItem in urlsItemInfos:
        urlItem['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

    #print(projectName, urlsItemInfos)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    #print('urlsItemInfos',urlsItemInfos)
    try:
        result1 = await createUrlItems(dbPrefix+'-'+projectId,'Urls',currentpage = currentPage, pagesize = pageSize,ItemInfos = urlsItemInfos)
    except pymongo.errors.BulkWriteError as e:
        # key重复错误， 返回重复的项
        # print(e.details['writeErrors'])
        temp = e.details['writeErrors']
        result = [] # 返回重复的项
        for ele in temp:
            result.append(ele['op']['rootUrl'])
        #print(result)
        raise HTTPException(status_code=503, detail="以下url重复，未插入,请修改后重试!" + str(result))
    except TypeError as e:
        print(e)
        raise HTTPException(status_code=503, detail='添加项不能为空')
    except Exception as e:
        # 其他错误
        print('ee',e)
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def get_urls(*,projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']) ,urlPart: Optional[str] = '', UrlId: Optional[str] = '', statusFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']),  currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询 url表中的数据
    # print(projectName,dateRange,urlPart, UrlId, currentPage,pageSize,statusFilter,categoryFilter)

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    #print(projectId)
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案
    if categoryFilter != ['']:
        categoryFilter =  unquote(categoryFilter[0], 'utf-8').split(',')
        #print(categoryFilter[0])
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')
        #print(type(statusFilter[0]))
    if dateRange != ['','']:
        dateRange = unquote(dateRange[0], 'utf-8').split(',')

    #print('projectName',projectName,'dateRange',dateRange,'urlPart',urlPart,'UrlId', UrlId,'currentPage', currentPage,'pageSize',pageSize,'statusFilter',statusFilter,'categoryFilter',categoryFilter)

    # 初始化 queryDict ，shownDict
    queryDict={}
    shownDict={}

    # 1- url 关键字搜索
    # 配置 queryDict 和 showDict ，依据 目的的不同
    if urlPart and not urlPart.startswith('*') and not urlPart.startswith('?') and not urlPart.startswith('+') and not urlPart.startswith('(') and not urlPart.startswith(')') and not urlPart.endswith('&\\'):
        # 有url 关键词查询
        if len(urlPart) == urlPart.count('\\') and len(urlPart)%2 == 1:
            urlPart = urlPart + '\\'
        queryDict['rootUrl']={'$regex':urlPart,'$options':'i'} # 查询包含，且不区分大小写 ,
        #queryDict['rootUrl']=json.loads(f'{{"$regex":/{urlPart}/,"$options":"i"}}')
        # shownDict['_id'] = 1
        # shownDict['rootUrl'] = 1
        pass
    else:
        # 无 url 关键词查询
        pass
        
    
    # 2- url uid 精准搜索 , url关键字搜索和 uid 精准搜索 每次搜索 只能选其一
    if UrlId:
        # urlid 精准查找
        try:
            oid = ObjectId(UrlId)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            queryDict['_id'] = oid
    else:
        pass
    # 3- categoryFilter 处理
    if categoryFilter !=['']:
        # 存在 categoryFilter 查询
         queryDict['category'] = {'$elemMatch':{'$in':categoryFilter}}
    else:
        pass
    # 4- statusFilter 处理
    if statusFilter != ['']:
        # 存在daterange
         queryDict['status'] = {'$in':statusFilter}
    else:
        # 不存在 daterange
        pass

    # 5- dateRange

    if dateRange != ['','']:
        # 存在 statusFilter 查询
        queryDict['modifiedTime'] = {'$gte':dateRange[0],'$lt':dateRange[1]}
    else:
        pass

    #print('queryDict',queryDict,shownDict)
    result = await fetchUrlItems(dbPrefix+'-'+projectId,'Urls',xfilter=queryDict,xshown =shownDict,  currentpage=currentPage,pagesize=pageSize)
    #print(result)
    return (result)


@router.get("/es/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def get_urls(*,projectName: str = Path(...), dateRange: Optional[List[str]] = Query(['','']) ,urlPart: Optional[str] = '', UrlId: Optional[str] = '', statusFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']), highlight: Optional[List[str]] = Query(['']), showReturn: Optional[List[str]] = Query(['']), currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询 url表中的数据
    # print(projectName,dateRange,urlPart, UrlId, currentPage,pageSize,statusFilter,categoryFilter)

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    #print(projectId)
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

     # 页码起始
    start = 0
    end = 0
    # 带搜索的 es索引 (等价于 mongo中的 数据库)
    _index = f'kwm-{projectId}.urls'.lower()
    #print('_index', _index)
    

    ## 首先，更新 index 的 mapping，添加 {'fielddata':True} , 使得 word 和 topicWord字段，可以 整体进行操作
    #xindex = Index(_index, using=esconnection)
    ## 给 topicWord 和 word字段 添加 "fielddata": True 属性
    #xindex.put_mapping(using=esconnection, body={"properties": {"rootUrl": {"type": "text", "fielddata": True}}})

    s = Search()

    #wordPart
    if urlPart:  # 通配符 匹配查询
        # 按照url 分隔符进行 分组: '/'
        urlPart = urlPart.replace(':', '')
        urlParts = urlPart.split('/')
        all = []
        for ele in urlParts:
            all.extend(ele.split('.'))
        q = ''
        for urlPart in all:
            if urlPart:
                q += f'Q("wildcard", rootUrl=f"*{urlPart.strip()}*") &' 
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
            

    # 排序设定: 构造 排序 表达式，如果存在排序的话
    s = s.source(includes=[])

     # 返回哪些字段
    if showReturn != ['']:
        showReturn = unquote(showReturn[0], 'utf-8').split(',')
        s = s.source(includes=showReturn)
    else:
        s = s.source(includes=[])

    # 高亮哪些字段
    if highlight != ['']:
    #highlight = ['rootUrl']
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
        #print('final',result)
        return ({'count': totalCount, 'content': result})



@router.put("/{projectName}/{urlID}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def update_url(*,projectName,urlID : str = Path(...),currentPage: int = 1, pageSize: int =10, urlsItemInfo:UrlsItemInfo):
    # Url表中添加 数据 
    # print(projectName, urlID, urlsItemInfo)
    urlsItemInfo = urlsItemInfo.dict()
    # 添加时间戳
    urlsItemInfo['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    #result1 = await createUrlItems(dbPrefix+'-'+projectId,'Urls',urlsItemInfos)
    
    # 生成urlID, 构造 querydict
    try:
        oid = ObjectId(urlID)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        urlID = oid
    # print('urlID',urlID)
    result1 = await updateUrlItems(dbPrefix+'-'+projectId,'Urls',currentPage = currentPage, pageSize = pageSize, queryDict={"_id":urlID},setDict={"$set":urlsItemInfo})
    #if 'error' in result1.lower():
    if isinstance(result1, str) and 'error' in result1.lower():
        raise HTTPException(status_code=503, detail=result1)
    else:
        return (result1)

async def update_Url_basd_url(projectName, allP):
    # 纯函数，基于 url 更新 项目状态

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    #result1 = await createUrlItems(dbPrefix+'-'+projectId,'Urls',urlsItemInfos)
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    
    # 循环更新
    for item in allP:
        # 添加时间戳
        item['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        queryBy = item.pop('queryBy')
        queryValue = item.pop('queryValue')
        result1 = await updateUrlItems(dbPrefix+'-'+projectId,'Urls',queryDict={queryBy:queryValue},setDict={"$set":item})
        #print('xxx',result1)
    return (result1)


@router.patch("/{projectName}/{urlID}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def update_url(*,projectName,urlID : str = Path(...), updateStatus:UpdateStatus):
    # Url表中修改数据
    #print(projectName, urlID, updateStatus)
    setDict = updateStatus.dict()
    # 添加时间戳
    setDict['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    #result1 = await createUrlItems(dbPrefix+'-'+projectId,'Urls',urlsItemInfos)
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    # 生成urlID, 构造 querydict
    try:
        oid = ObjectId(urlID)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        urlID = oid
    # print('urlID',urlID)
    # print(setDict)
    result1 = await updateUrlItems(dbPrefix+'-'+projectId,'Urls',queryDict={"_id":urlID},setDict={"$set":setDict})
    #print('xxx',result1)
    return (result1)


@router.delete("/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def delete_url(*,projectName: str = Path(...),urlID: List[str]):
    # 查询 url表中的数据,有可能有多个
    #print(projectName, urlID)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    deleteDictList = []
    for url in urlID:
        try:
            oid = ObjectId(url)
        except:
            raise HTTPException(status_code=503, detail='invalid ObjectID')
        else:
            deleteDict = {'_id': oid}
            deleteDictList.append(deleteDict)
    result = await deleteUrlItems(dbPrefix+'-'+projectId,'Urls',deleteDictList)
    return (result)

# @router.get("/{projectName}/Categories",dependencies=[Depends(verify_token)])
# async def fetchCategories(*,projectName: str = Path(...)):
#     # 查询Project Name下的所有 目录列表
#     print(projectName)
#     # projectName 转 projectId
#     projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
#     result = await getCategories(dbPrefix+'-'+projectId,'Categories')
#     #print('cccc',result)
#     return (result)