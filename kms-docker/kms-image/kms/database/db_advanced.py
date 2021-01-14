from .db_basic import dbinit, insert_one, insert_many, find, findCount, find_one, update_one, update_many, copy_database, drop_database, delete_one, check_collection_count, aggregate
import json
import pymongo
from bson import json_util
from utilities.jwtTools import createJWT, verifyJWT
from myExceptions import AccountNotExistError,PasswordMismatchError
import time

# 数据库结构概览:
# 数据库: keywordsManagement
#  ->表: User ,存储账户信息
#  ->表: Project, 存储项目概要信息，但不包含分类信息
# 数据库: 项目x: 每个项目一个数据库，每个数据库包含如下表
#  ->表: Categories
#  ->表: Urls
#  ->表: Articles
#  ->表: BasicWords
#  ->表: ExtendedWords
#  ->表: stopDict
#  ->表: invalidDict
#  ->表: userDict

# 数据库部分初始化操作
dbinit()
dbPrefix = 'KWM'

# Projects 相关 高级 函数
async def fetchAllProjects(currentpage=1, pagesize=10):
    # 1- 获取 Project表内容
    result1 = await fetchTable(dbPrefix, 'Project', currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print('result1',result1)
    # result1 形式:  result1 = {'count':count,'content':content}
    # 2- 因为category 跟 表 Project 是分开的，所以需要分开查找
    if result1['count'] > 0:
        # 存在项目，才去读项目中的 目录信息
        for project in result1['content']:
            # print('project',project)
            projectId = project['_id']['$oid']
            result2 = await fetchTable(dbPrefix + '-' + projectId, 'Categories', currentpage=0, pagesize=0, returnTotalCount=False)
            # print('xxxxxx',result2)
            project['categories'] = result2['content']
    return result1


async def createnewproject(dbName, collectionName, projectObjectData, currentpage=1, pagesize=10):
    # 1- 在Project表添加新项目，如果已经存在，则报错返回
    categotiesData = projectObjectData.pop('categories')
    try:
        result1 = await insert_one(dbName, collectionName, projectObjectData)
    except Exception as e:
        raise
    else:
        # 插入项目名称 成功
        #print('result1', result1)
        # 2-项目创建成功，则创建以该项目命名的数据库，并将Categories 写入 Categories 表格
        # dbName2 = projectObjectData['projectName']
        # 使用uuid代表真正的项目名称，并创建项目
        dbName2 = str(result1)
        #print('dbName2', dbName2)
        result2 = ''
        if len(categotiesData) > 0:
            # 只有设置了目录元素的时候才进行插入，否则，什么都不做
            # print('dbName2',dbName2)
            try:
                result2 = await insert_many(dbPrefix + '-' + dbName2, 'Categories', categotiesData)
            except Exception as e:
                raise
            #print('result2', result2)
        else:
            result2 = 0
            #print('result2', result2)
        # 如果都成功，返回 新的数据
        return await fetchAllProjects(currentpage=currentpage, pagesize=pagesize)


async def fetchTable(dbName, collectionName, idPrefix="", xfilter={}, xshown={}, xsort=[], currentpage=1, pagesize=10, returnTotalCount=True):
    if returnTotalCount:
        # 1 读取所有项目数目
        result1 = await findCount(dbName, collectionName, xfilter)
        # 此处 result1 肯定是个数字， 0 或者  >0
    else:
        result1 = ''

    # 2 读取所有的表信息
    result2 = []
    if (type(result1) == int and result1 > 0) or result1 == '':
        # 1-1: 存在数据，则继续下一步 1-2: 没有计算长度 ，也进入下一步。 否则，直接返回空
        skipValue = (currentpage - 1) * pagesize
        limitValue = pagesize
        result2 = json.loads(await find(dbName, collectionName, xfilter=xfilter, xshown=xshown, xsort=xsort, skipValue=skipValue, limitValue=limitValue))
        # 添加 ID
        initID = 1
        if idPrefix == '':
            for ele in result2:
                ele['id'] = skipValue + initID
                initID += 1
        else:
            # id 西药添加特定前缀
            for ele in result2:
                ele['id'] = str(idPrefix) + '-' + str(skipValue + initID)
                initID += 1
        # print('xxxx',result2)
    return ({'count': result1, 'content': result2})


async def updateProject(dbName, collectionName, queryDict={}, setDict={},currentPage=1, pageSize=10):
    # print(setDict)
    # 1- 更新特定醒目名称信息
    try:
        result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    except:
        raise
    else:
        # 修改 项目数据库列表成功
        return await  fetchAllProjects(currentpage=currentPage, pagesize=pageSize)



async def deleteProject(dbName, collectionName, queryDict={},currentPage=1,pageSize=10):
    projectId = queryDict['_id']
    # 1: 删除项目列表中的 项目名称
    result1 = await delete_one(dbName, collectionName, queryDict)
    if result1 == 1:
        # step1 修改成功
        # 2: 删除项目数据库
        projectid = json.loads(json_util.dumps(projectId))['$oid']
        result2 = await drop_database(dbPrefix + '-' + projectid)
        if not result2:
            # 删除数据库成功
            # 3- 拉取所有数据
            result3 = await fetchAllProjects(currentpage=currentPage, pagesize=pageSize)
            return (result3)
        else:
            return ('error')
    else:
        return ('error')


async def updateCategory(dbName, collectionName, queryDict={}, setDict={},currentPage = 1, pageSize= 10):
    # 更新特定项目中的 目录
    # 1- 更新 对应项目，分类表中的数据
    try:
        result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    except:
        raise
    else:
        if result1 == 1:
            # 1- 修改 项目数据库列表成功
            # 2- 拉取所有数据
            result2 = await fetchAllProjects(currentpage=currentPage, pagesize=pageSize)
            return (result2)
        else:
            pass

async def deleteCategory(dbName, collectionName, queryDict={},currentPage=1,pageSize=10):
    # 1: 删除项目列表中的 项目名称
    try:
        result1 = await delete_one(dbName, collectionName, queryDict=queryDict)
    except:
        raise
    else:
        result2 = await fetchAllProjects(currentpage=currentPage, pagesize=pageSize)
        return (result2)

async def createCategory(dbName, collectionName, setDict={},currentPage=1,pageSize=10):
    # 创建 目录
    try:
        result1 = await insert_one(dbName, collectionName, data = setDict)
    except:
        raise
    else:
        # 创建成功，刷新所有 projects信息
        return  await fetchAllProjects(currentpage=currentPage, pagesize=pageSize)

async def handleSignup(dbName, collectionName, accountInfo):
    """
        处理用户注册
    """

    # 1 - 直接注册，父函数 根据结果，做出相应 判断
    try:
        result1 = await insert_one(dbName, collectionName, accountInfo)
    except:
        raise
    else:
        return ('注册成功')


async def handleSignin(dbName, collectionName, accountInfo):
    """
        处理用户登录
    """
    # 1 检查账号是否存在
    try:
        result1 = await find_one(dbName, collectionName, queryDict={'account': accountInfo['account']})
    except:
        raise
    else:
        if result1 == 'null':
            # 账号不存在,抛出异常
            raise AccountNotExistError(f'账号{accountInfo["account"]}未注册!')
        else:
            # 用户已经注册，继续向下
            # 2- 如果存在，检查账号密码是否一致
            try:
                result2 = await find_one(dbName, collectionName, queryDict={'account': accountInfo['account'], 'shadow': accountInfo['shadow']})
            except:
                raise
            else:
                if result2 == 'null':
                    # 账号密码不一致：密码错误
                    raise PasswordMismatchError(f'账号{accountInfo["account"]}密码错误，请重试!')
                else:
                    # 3- 密码正确， 继续，获取用户部门信息
                    try:
                        result3 = await find_one(dbName, collectionName, queryDict={'account': accountInfo['account']}, showDict={'_id': 0, 'department': 1})
                    except:
                        raise
                    else:
                        # 部门信息ok，生成JWT
                        try:
                            jwttoken = await createJWT({'name': accountInfo['account']})
                        except:
                            raise
                        else:
                            return ({"username": accountInfo['account'], "access_token": str(jwttoken, 'utf-8'), "token_type": "bearer", "department": json.loads(result3)['department']})


# Urls related high level functions
async def createUrlItems(dbName, collectionName, currentpage=1, pagesize=10, ItemInfos={}):
    # 直接使用 insert_many
    try:
        result1 = await insert_many(dbName, collectionName, data2insert=ItemInfos)
    except Exception as e:
        raise
    else:
        print('no error')
        # if isinstance(result1, int):
        print('插入成功')
        # 获取所有数据(首页) 返回
        # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
        return (result2)
        # else:
        #    return(result1)

# async def createUrlItems(dbName, collectionName, ItemInfos):
#     # 直接使用 insert_many
#     result1 = await insert_many(dbName, collectionName, ItemInfos)
#     if isinstance(result1, int):
#         print('插入成功')
#         # 获取所有数据(首页) 返回
#         # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
#         result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=1, pagesize=10, returnTotalCount=True)
#         return (result2)
#     else:
#         return('error')

# async def updateUrlItems(dbName,collectionName,queryDict={},setDict={}):
#    #print('setDict',dbName,collectionName,setDict,queryDict,pageSize,currentPage)
#


async def updateUrlItems(dbName, collectionName, queryDict={}, setDict={}, pageSize=10, currentPage=1):
    # print('setDict',dbName,collectionName,setDict,queryDict,pageSize,currentPage)
    print('++++++++++++++', dbName, collectionName,
          setDict, queryDict, pageSize, currentPage)
    result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    # print('result1',result1)
    if result1 == 1:
        print('插入成功')
        # 获取所有数据(首页) 返回
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pageSize, returnTotalCount=True)
        return (result2)

    else:
        return(result1)


async def findProjectIdFromProjectName(dbName, collectionName, queryDict={}, showDict={}):
    print('queryDict', queryDict)
    result1 = json.loads(await find_one(dbName, collectionName, queryDict, showDict))
    # print('result1',result1)
    if result1:
        projectId = result1['_id']['$oid']
        return projectId
    else:
        return None


async def fetchUrlItems(dbName, collectionName, xfilter={}, xshown={}, currentpage=1, pagesize=10, returnTotalCount=True):
    # 获取 特定项目 Url表中符合条件的数据
    result1 = await fetchTable(dbName, collectionName, xfilter=xfilter, xshown=xshown, currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print(result1,type(result1))
    return result1


async def deleteUrlItems(dbName, collectionName, deleteDictList=[]):
    if deleteDictList == []:
        # 什么也不删除
        return ('error')
    else:
        # 循环删除
        try:
            for ele in deleteDictList:
                print(ele)
                result1 = await delete_one(dbName, collectionName, ele)
            # 成功，刷新列表
            result2 = await fetchTable(dbName, collectionName)
            return (result2)
        except:
            return ('error')


async def getCategories(dbName, collectionName):
    print(dbName, collectionName)
    try:
        result = await fetchTable(dbName, collectionName, xshown={'_id': 0, 'categoryName': 1}, returnTotalCount=False, currentpage=0, pagesize=0)
    except:
        raise
    else:
        return(result)

"""
停止词,用户词和无效词共用部分
"""

async def fetchDictItems(dbName, collectionName, xfilter={}, xshown={}, currentpage=1, pagesize=10, returnTotalCount=True):
    # 获取 特定项目 Url表中符合条件的数据
    result1 = await fetchTable(dbName, collectionName, xfilter=xfilter, xshown=xshown, currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print(result1,type(result1))
    return result1


async def createDictItems(dbName, collectionName, currentpage=1, pagesize=10, ItemInfos={}):
    # 直接使用 insert_many
    try:
        result1 = await insert_many(dbName, collectionName, data2insert=ItemInfos)
    except:
        raise
    else:
        print('插入成功')
        # 获取所有数据(首页) 返回
        # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
        return (result2)


async def updateDictItems(dbName, collectionName, queryDict={}, setDict={}, pageSize=10, currentPage=1):
    try:
        result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    except:
        raise
    else:
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pageSize, returnTotalCount=True)
        return (result2)


async def deleteDictItems(dbName, collectionName, deleteDictList=[]):
    if deleteDictList == []:
        # 什么也不删除
        return ('error')
    else:
        # 循环删除
        try:
            for ele in deleteDictList:
                result1 = await delete_one(dbName, collectionName, ele)
                if result1:
                    pass
            # 成功，刷新列表
            result2 = await fetchTable(dbName, collectionName)
            return (result2)
        except:
            return ('error')


async def ItemExist(dbName, collectionName, filter={}):
    return await find_one(dbName, collectionName, filter)


async def check_if_collection_is_empty(dbName, collectionName):
    return await check_collection_count(dbName, collectionName)

"""
用户词相关
"""


async def deleteUserDictItems(dbName, collectionName, targetCollection, currentpage, pagesize, sourceList=[], targetList=[]):
    if sourceList == []:
        # 什么也不删除
        return ('error')
    else:
        # 循环删除
        try:
            for i in range(len(sourceList)):
                result = await insert_one(dbName, targetCollection, data=targetList[i])
                if result != 'project-unknownError':
                    result1 = await delete_one(dbName, collectionName, sourceList[i])
                else:
                    return ('error')
            # 成功，刷新列表
            result2 = await fetchTable(dbName, collectionName)
            return (result2)
        except:
            return ('error')


async def getFieldFromCollection(dbName, collectionName, field, filter={}):
    data = await find_one(dbName, collectionName, filter)
    return json.loads(data)[field] if data else ''


# articles related
async def createArticleItems(dbName, collectionName, currentpage=1, pagesize=10, ItemInfos={}):
    # 直接使用 insert_many
    try:
        result1 = await insert_many(dbName, collectionName, data2insert=ItemInfos)
    except Exception as e:
        raise
    else:
        # if isinstance(result1, int):
        print('插入成功')
        # 获取所有数据(首页) 返回
        # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
        return (result2)


async def getArticles(dbName, collectionName, xfilter={}, xshown={}, currentpage=1, pagesize=10, returnTotalCount=True):
    # 获取 特定项目 Url表中符合条件的数据
    result1 = await fetchTable(dbName, collectionName, xfilter=xfilter, xshown=xshown, currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print(result1,type(result1))
    return result1


async def getArticleBody(dbName, collectionName, xfilter={}, xshown={}, currentpage=1, pagesize=10, returnTotalCount=True):
    # 获取 特定项目 Url表中符合条件的数据
    result1 = await fetchTable(dbName, collectionName, xfilter=xfilter, xshown=xshown, currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print(result1,type(result1))
    return result1


async def deleteArticleItems(dbName, collectionName, deleteDictList=[]):
    if deleteDictList == []:
        # 什么也不删除
        return ('error')
    else:
        # 循环删除
        try:
            for ele in deleteDictList:
                # print(ele)
                result1 = await delete_one(dbName, collectionName, ele)
            # 成功，刷新列表
            result2 = await fetchTable(dbName, collectionName)
            return (result2)
        except:
            return ('error')


async def updateArticleSplitWords(dbName, collectionName, queryDict={}, setDict={}, pageSize=10, currentPage=1):
    # print('setDict',dbName,collectionName,setDict,queryDict,pageSize,currentPage)
    print('++++++++++++++', dbName, collectionName,
          setDict, queryDict, pageSize, currentPage)
    result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    # print('result1',result1)
    if result1 == 1:
        print('插入成功')
        # 获取所有数据(首页) 返回
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pageSize, returnTotalCount=True)
        return (result2)

    else:
        return(result1)

"""
用户相关
"""


async def fetchUsers(dbName, collectionName, showDict={},currentPage=1, pageSize=1000):
    result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown=showDict, xsort=[], currentpage=currentPage, pagesize=pageSize, returnTotalCount=True)
    return (result2)


"""
basicWords related
"""


async def addBasicWords(dbName, collectionName, currentPage=1, pagesize=10, ItemInfos={}):
    # 直接使用 insert_many
    try:
        result1 = await insert_many(dbName, collectionName, data2insert=ItemInfos)
    except Exception as e:
        raise
    else:
        # if isinstance(result1, int):
        print('插入成功')
        # 获取所有数据(首页) 返回
        # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pagesize, returnTotalCount=True)
        return (result2)


async def fetchBasicWords(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=1, pagesize=10, returnTotalCount=True):
    # 获取 特定项目 basicWords 表中符合条件的数据
    # print(dbName,collectionName,xfilter,xshown)
    result1 = await fetchTable(dbName, collectionName, xfilter=xfilter, xshown=xshown, xsort=xsort, currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print(result1,'ccccccc')
    return result1


async def deleteBacisWordsItems(dbName, collectionName, deleteDictList=[]):
    if deleteDictList == []:
        # 什么也不删除
        return ('error')
    else:
        # 循环删除
        try:
            for ele in deleteDictList:
                # print(ele)
                result1 = await delete_one(dbName, collectionName, ele)
            # 成功，刷新列表
            result2 = await fetchTable(dbName, collectionName)
            return (result2)
        except:
            return ('error')


async def updateBasicWords(dbName, collectionName, queryDict={}, setDict={}, pageSize=10, currentPage=1):
    # print('setDict',dbName,collectionName,setDict,queryDict,pageSize,currentPage)
    print (dbName, collectionName,
          setDict, queryDict, pageSize, currentPage)
    result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    # print('result1',result1)
    if result1 == 1:
        print('插入成功')
        # 获取所有数据(首页) 返回
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pageSize, returnTotalCount=True)
        return (result2)
    else:
        return(result1)

"""
extendedWords related
"""


async def addExtendedWords(dbName, collectionName, currentPage=1, pagesize=10, ItemInfos={}):
    # 直接使用 insert_many
    try:
        result1 = await insert_many(dbName, collectionName, data2insert=ItemInfos)
    except Exception as e:
        raise
    else:
        print('插入成功')
        # 获取所有数据(首页) 返回
        # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pagesize, returnTotalCount=True)
        return (result2)


async def fetchExtendedWords(dbName, collectionName, idPrefix='',xfilter={}, xshown={}, xsort=[], currentpage=1, pagesize=10, returnTotalCount=True):
    # 获取 特定项目 extendedWords 表中符合条件的数据
    result1 = await fetchTable(dbName, collectionName, idPrefix= idPrefix,xfilter=xfilter, xshown=xshown, xsort=xsort, currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    # print(result1,type(result1))
    return result1


async def makeAggregations(dbName, collectionName, currentPage=1, pageSize = 10, xaggregate= [],types='topicWord',returnTotalCount=True):
    """
        获取 聚合数据 以及 符合条件的 数据总 数量，类似于 fetchTable
    """

    # 构造 skip 和 limit
    skip = (currentPage - 1) * pageSize
    limit = pageSize

    if types == 'mword':
        # 只要 获取 到 mword，就行了，PVsum avg等职能通过 sub 相加，在前端
        print('xaggregate0000',xaggregate)
        #yxaggregate = []
        #yxaggregate.append({'$match': xaggregate[0]['$match']})
        #yxaggregate.append({'$group': {'_id':xaggregate[1]['$group']['_id']}})
        ## 在  yxaggregate ，中添加 '$count' 算子,
        #yxaggregate.append({'$count': 'totalCount'})
        result1 = list(await aggregate(dbName, collectionName, aggregation=xaggregate))

        # 添加 ID
        initID = 1
        for ele in result1:
            ele['word'] = ele.pop('_id')[types]
            ele['id'] = skip+ initID
            ele['_loading']= False
            ele['children'] = []
            initID += 1
        print('result1',result1)
        return {'count': len(result1),'content':result1}

    if returnTotalCount:
        # 1 读取所有项目数目，首先构建 ，只查询项目 数目的 查询表达式
        yxaggregate = []
        print('xaggregatemmm',xaggregate)
        if xaggregate[0]['$match']:
            yxaggregate.append({'$match': xaggregate[0]['$match']})
        if xaggregate[1].get('$group') and xaggregate[1].get('$group').get('_id'):
            yxaggregate.append({'$group': {'_id':xaggregate[1]['$group']['_id']}})

        # 在  yxaggregate ，中添加 '$count' 算子,
        yxaggregate.append({'$count': 'totalCount'})
        print('yxaggregate',yxaggregate)
        result1 = list(await aggregate(dbName, collectionName, aggregation=yxaggregate))
        
        if len(result1) == 0:
            #返回0， 并退出
            return ({'count': 0, 'content': []})
        else:
            result1 =  result1[0]['totalCount']
        # 此处 result1 肯定是个数字， 0 或者  >0
    else:
        result1 = ''
    print('result1vvv',result1)
    # 2 读取所有的表信息
    result2 = []
    if (type(result1) == int and result1 > 0) or result1 == '':
        # 1-1: 存在数据，则继续下一步 1-2: 没有计算长度 ，也进入下一步。 否则，直接返回空

        # xaggregate.append({'$skip': skip}) # 获取全部数据，不需要分页
        # xaggregate.append({'$limit': limit})
        
        print('xaggregate',xaggregate)
        result2 = list(await aggregate(dbName, collectionName, aggregation=xaggregate))
        print('hello',result2) 
    return (json.loads(json_util.dumps({'count': result1, 'content': result2})))


async def fetchExtendedWordsTopic(dbName, collectionName,  currentPage=1, pageSize = 10,xaggregate =[],returnTotalCount=True):
    # 获取 特定项目 extendedWords 表中符合条件的  主题词 聚合 数据 
    result1 = await makeAggregations (dbName, collectionName, currentPage=currentPage, pageSize = pageSize, xaggregate=xaggregate, returnTotalCount=True)
    # print(result1,type(result1))
    return result1

async def fetchExtendedWordsInherit(dbName, collectionName,  currentPage=1,pageSize = 10, xaggregate =[],returnTotalCount=True):
    # 获取 特定项目 extendedWords 表中符合条件的  主题词 聚合 数据
    result1 = await makeAggregations (dbName, collectionName, currentPage=currentPage, types='mword',pageSize = pageSize, xaggregate=xaggregate, returnTotalCount=True)
    # print(result1,type(result1))
    return result1

async def deleteExtendedWordsItems(dbName, collectionName, deleteDictList=[]):
    if deleteDictList == []:
        # 什么也不删除
        return ('error')
    else:
        # 循环删除
        try:
            for ele in deleteDictList:
                # print(ele)
                result1 = await delete_one(dbName, collectionName, ele)
            # 成功，刷新列表
            result2 = await fetchTable(dbName, collectionName)
            return (result2)
        except:
            return ('error')


async def updateExtendedWords(dbName, collectionName, updateType='one',queryDict={}, setDict={}, pageSize=10, currentPage=1):
    # print('setDict',dbName,collectionName,setDict,queryDict,pageSize,currentPage)
    print('++++++++++++++', dbName, collectionName,
          setDict, queryDict, pageSize, currentPage)
    if updateType == 'many':
        result1 = await update_many(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    else:
        result1 = await update_one(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    #result1 = await update_many(dbName, collectionName, queryDict=queryDict, setDict=setDict)
    print('result1',result1)
    if result1 >= 1:
        print('插入成功')
        # 获取所有数据(首页) 返回
        result2 = await fetchTable(dbName, collectionName, xfilter={}, xshown={}, xsort=[], currentpage=currentPage, pagesize=pageSize, returnTotalCount=True)
        return (result2)
    else:
        return(result1)

'''
标签云相关
'''


async def fetchUsageTags(dbName, collectionName):
    usageTags = await find(dbName, collectionName)
    return usageTags


if __name__ == '__main__':
    update_one('KWM-5f5c4240e0c234a92a524a36', 'StopDict', {'_id': '5f5cdc64041c89a528d10776'}, {
               '$set': {'word': '测试qweqweqweqwe', 'modifiedTime': '2020-09-12 22:49:27'}})
