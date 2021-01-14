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
from database.db_advanced import createUrlItems, findProjectIdFromProjectName,fetchUrlItems,updateUrlItems, deleteUrlItems, getCategories
from utilities.jwtTools import verify_token


from elasticsearch_dsl import connections, Search



router = APIRouter()
dbPrefix = 'KWM'
esconnection = 'es7_connection'

connections.create_connection(hosts=['localhost'], timeout=60)

class UrlPath(BaseModel):
    path: str = Query(None, min_length=7, max_length=250,regex="^https?://")
    type: str = Query(None, min_length=2, max_length=250,regex="^包含$|^regex$")

class UrlsItemInfo(BaseModel):
    # UpdateCategory body数据模型
    rootUrl: str = Query(None, min_length=7, max_length=250,regex="^https?://")
    #category: List[str] = Query([],min_length=1)
    category: conlist(str, min_items = 1)
    status: str
    urlExcludePath: List[UrlPath]
    urlIncludePath: List[UrlPath]

class UpdateStatus(BaseModel):
    status: str

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

@router.post("/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def create_url(*,projectName: str = Path(...),currentPage: int = 1, pageSize: int =10, urlsItemInfos:List[UrlsItemInfo]):
    # Url表中添加 数据 
    # print(projectName, urlsItemInfos)
    urlsItemInfos = [urlsItem.dict() for urlsItem in urlsItemInfos]
    # 添加时间戳
    for urlItem in urlsItemInfos:
        urlItem['modifiedTime'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
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
        #print(e)
        raise HTTPException(status_code=503, detail='添加项不能为空')
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=503, detail=json.loads(json_util.dumps(e.details)))
    else:
        return (result1)


@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["Urls"])
async def get_urls(*,projectName: str = Path(...), dataRange: Optional[List[str]] = Query(['','']) ,urlPart: Optional[str] = '', UrlId: Optional[str] = '', statusFilter: Optional[List[str]] = Query(['']), categoryFilter: Optional[List[str]] = Query(['']),  currentPage: Optional[int] = 1, pageSize: Optional[int] =10):
    # 查询 url表中的数据
    # print(projectName,dataRange,urlPart, UrlId, currentPage,pageSize,statusFilter,categoryFilter)

    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    print(projectId)
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')

    # decodeURIComponent ，前端发过来的数据已经编程字符串了，所以需要先 decode，再转换成数组。暂时还没找到更好的解决方案
    if categoryFilter != ['']:
        categoryFilter =  unquote(categoryFilter[0], 'utf-8').split(',')
        #print(categoryFilter[0])
    if statusFilter != ['']:
        statusFilter = unquote(statusFilter[0], 'utf-8').split(',')
        #print(type(statusFilter[0]))
    if dataRange != ['','']:
        dataRange = unquote(dataRange[0], 'utf-8').split(',')

    print('projectName',projectName,'dataRange',dataRange,'urlPart',urlPart,'UrlId', UrlId,'currentPage', currentPage,'pageSize',pageSize,'statusFilter',statusFilter,'categoryFilter',categoryFilter)

    # 初始化 queryDict ，shownDict
    queryDict={}
    shownDict={}

    # 1- url 关键字搜索
    # 配置 queryDict 和 showDict ，依据 目的的不同
    if urlPart and not urlPart.startswith('*'):
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

    # 5- dataRange

    if dataRange != ['','']:
        # 存在 statusFilter 查询
        queryDict['modifiedTime'] = {'$gte':dataRange[0],'$lt':dataRange[1]}
    else:
        pass

    print('queryDict',queryDict,shownDict)
    result = await fetchUrlItems(dbPrefix+'-'+projectId,'Urls',xfilter=queryDict,xshown =shownDict,  currentpage=currentPage,pagesize=pageSize)
    #print(result)
    return (result)



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