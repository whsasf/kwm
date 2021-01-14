import pymongo
import json
from bson import json_util
from elasticsearch_dsl import connections, Search

# elastic search connection
esconnection = 'es7_connection'


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
#import socket
#
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.connect(("8.8.8.8", 80))
#ipaddr = s.getsockname()[0]
# s.close()

# 启动 elactic Search 连接

try:
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    #client = pymongo.MongoClient('mongodb://root:sccgoodToGo@114.67.109.244:27017/')
    print('mongodb连接成功')
except Exception as e:
    print(e)
else:
    dbPrefix = 'KWM'  # keywordsManagement


def dbinit():
    """
    初始化一些数据库或collection,不是非得做，mongo会自动创建不存在的数据库和collection。
    但是为了流程考虑，暂时保留该步骤。具体如下:
    1 数据库: keywordsManagement  -> User | Project
    2 keywordsManagement -> Project 表中定义的各个数据库 
    """
    print('<<-dbinit begin ...')

    # find localhost IP

    keywordsmanagementDbHandler = client[dbPrefix]
    # 1 数据库: keywordsManagement  -> User | Project
    keywordsManagementDbCollections = keywordsmanagementDbHandler.list_collection_names()
    for element in ['User', 'Project']:
        if element in keywordsManagementDbCollections:
            print(f"表{element}在数据库keywordsManagement中存在")
        else:
            print(f"表{element}在数据库keywordsManagement中不存在,创建中 ...")
            # 创建表
            try:
                keywordsmanagementDbHandler.create_collection(element)
            except Exception as e:
                print(e)

        # Project表 将 name设成唯一性索引, User 表，将account字段设成唯一索引
        keywordsmanagementDbHandler.Project.create_index(
            [("projectName", 1)], unique=True, background=True)
        keywordsmanagementDbHandler.User.create_index(
            [("account", 1)], unique=True, background=True)

    # 2 keywordsManagement -> Project 表中定义的各个数据库
    # 获取所有项目名称列表
    projectNameIds = keywordsmanagementDbHandler['Project'].find(
        {}, {"_id": 1}).sort('timestamp', -1)
    print(list(projectNameIds))
    for element in projectNameIds:
        # 创建每一个数据库,如果不存在; 并将每个项目中， Categories 表设成 name 字段的唯一性索引, 在Article 中，将 url设成 唯一索引;Url 表中，将 rooturl设成唯一性索引
        client[dbPrefix + '-' + str(element['_id'])]['Categories'].create_index(
            [("categoryName", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['Articles'].create_index([
            ("url", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['Urls'].create_index(
            [("rootUrl", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['basicWords'].create_index([
            ("word", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['extendedWords'].create_index([
            ("word", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['StopDict'].create_index([
            ("word", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['InvalidDict'].create_index([
            ("word", 1)], unique=True, background=True)
        client[dbPrefix + '-' + str(element['_id'])]['UserDict'].create_index([
            ("word", 1)], unique=True, background=True)

    print('dbinit end ...>>')
    print('<< ...elastic search init begin')
    connections.create_connection(alias=esconnection, hosts=['localhost'], timeout=60)
    print('elastic search init end ...>>')


async def esRun(params,index):
    #print('params,index',params,index)
    s = Search.from_dict(params).using(esconnection).index(index)
    #print('sss', s)
    try:
        result =  s.execute(ignore_cache=True)
    except Exception as e:
        result = e
    finally:
        #print(result)
        return result

async def list_collection_names(dbName, collectionName):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    return collectionHandler.list_collection_names()


async def es_find(_index,):
    """
        从 elastic search 中 查找所有符合条件的数据行
        输入参数:
        _index: 要检索的索引。等价于 数据库

    """


async def aggregate(dbName, collectionName,aggregation=[]):
    """
    执行 mongodb 聚合 查询操作
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result =  collectionHandler.aggregate(aggregation)
    except:
        raise
    else:
        return result


async def find(dbName, collectionName, xfilter={}, xshown={}, xsort=[], skipValue=0, limitValue=0):
    """
    查找所有符合条件的数据行
    dbName:  dbname
    collectionName: collection name
    xfilter: 查询字段 {'name':'ram'}
    xshown: 需要过滤返回的字段 {'_id':0,name:1}  代表只返回 name字段
    xsort： 需要排序的字段以及排序方式 [(a,1),(b,-1)]
    skipValue： skip的数目
    limitValue: 返回的数目
    """

    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    if xshown == {}:  # 全部字段显示返回
        if xsort == []:  # 无排序
            result = json_util.dumps(collectionHandler.find(
                xfilter).skip(skipValue).limit(limitValue))
        else:  # 有排序
            result = json_util.dumps(collectionHandler.find(
                xfilter).sort(xsort).skip(skipValue).limit(limitValue))
    else:  # 筛选返回
        if xsort == []:  # 无排序
            result = json_util.dumps(collectionHandler.find(
                xfilter, xshown).skip(skipValue).limit(limitValue))
        else:  # 有排序
            result = json_util.dumps(collectionHandler.find(
                xfilter, xshown).sort(xsort).skip(skipValue).limit(limitValue))
    return result


#async def find_one(dbName, collectionName, xfilter={}, xshown={}, xsort=[], skipValue=0, limitValue=1):
#    """
#    查找第一个符合条件的数据行
#    dbName:  dbname
#    collectionName: collection name
#    xfilter: 查询字段 {'name':'ram'}
#    xshown: 需要过滤返回的字段 {'_id':0,name:1}  代表只返回 name字段
#    xsort： 需要排序的字段以及排序方式 [(a,1),(b,-1)]
#    skipValue： skip的数目
#    limitValue: 返回的数目
#    """
#
#    dbHandler = client[dbName]
#    collectionHandler = dbHandler[collectionName]
#    try:
#        if xshown == {}:  # 全部字段显示返回
#            if xsort == []:  # 无排序
#                result = json_util.dumps(collectionHandler.find(
#                    xfilter).skip(skipValue).limit(limitValue))
#            else:  # 有排序
#                result = json_util.dumps(collectionHandler.find(
#                    xfilter).sort(xsort).skip(skipValue).limit(limitValue))
#        else:  # 筛选返回
#            if xsort == []:  # 无排序
#                result = json_util.dumps(collectionHandler.find(
#                    xfilter, xshown).skip(skipValue).limit(limitValue))
#            else:  # 有排序
#                result = json_util.dumps(collectionHandler.find(
#                    xfilter, xshown).sort(xsort).skip(skipValue).limit(limitValue))
#    except:
#        raise
#    else:
#        return result


async def findCount(dbName, collectionName, xfilter={}):
    """
    查找所有符合条件的 文档的数目
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    result = collectionHandler.find(xfilter).count()
    print(f'{dbName}->{collectionName}总共有{result}条符合条件的数据')
    return result


async def find_one(dbName, collectionName, queryDict={}, showDict={}):
    """
    查找第一个符合条件的数据行
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        if queryDict == {}:
            if showDict == {}:
                result = json_util.dumps(collectionHandler.find_one())
            else:
                result = json_util.dumps(collectionHandler.find_one({}, showDict))
        else:
            if showDict == {}:
                result = json_util.dumps(collectionHandler.find_one(queryDict))
            else:
                result = json_util.dumps(
                    collectionHandler.find_one(queryDict, showDict))
    except:
        raise
    else:
        return result


async def insert_one(dbName, collectionName, data={}):
    """
    数据库表中插入 单行数据
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]

    # 确保唯一性
    if collectionName == 'Categories':
        collectionHandler.create_index(
            [('categoryName', 1)], unique=True, background=True)
    elif collectionName == 'User':
        collectionHandler.create_index(
            [('account', 1)], unique=True, background=True)
    elif collectionName == 'Urls':
        collectionHandler.create_index(
            [('rootUrl', 1)], unique=True, background=True)
    elif collectionName in ['basicWords', 'extendedWords']:
        collectionHandler.create_index(
            [('word', 1)], unique=True, background=True)
    elif collectionName == 'Articles':
        #collectionHandler.create_index([('url',1)],unique = True, partialFilterExpression={'url':{'$type': 'string'}}, background = True)
        collectionHandler.create_index(
            [('url', 1)], unique=True, background=True)
    elif collectionName in ['StopDict', 'InvalidDict', 'UserDict']:
        collectionHandler.create_index(
            [('word', 1)], unique=True, background=True)

    # try:
    # 将所有异常处理，返回给上级
    try:
        result = collectionHandler.insert_one(data)
        # print(result.inserted_id)
        # 成功: 返回插入的数据个数,此处为1
    except:
        raise
    else:
        return result.inserted_id
    #    return ([result.inserted_id])
    # except pymongo.errors.DuplicateKeyError as e:
    #    print('error:',e)
    #    return ('duplicateError-projectName')
    # except Exception as e:
    #    print('error:',e)
    #    return ('project-unknownError')


async def insert_many(dbName, collectionName, data2insert={}):
    """
    数据库表中插入 多行数据
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    if collectionName == 'Categories':
        collectionHandler.create_index(
            [('categoryName', 1)], unique=True, background=True)
    elif collectionName == 'User':
        collectionHandler.create_index(
            [('account', 1)], unique=True, background=True)
    elif collectionName == 'Urls':
        collectionHandler.create_index(
            [('rootUrl', 1)], unique=True, background=True)
    elif collectionName in ['basicWords', 'extendedWords']:
        collectionHandler.create_index(
            [('word', 1)], unique=True, background=True)
    elif collectionName == 'Articles':
        collectionHandler.create_index(
            [('url', 1)], unique=True, background=True)
    elif collectionName in ['StopDict', 'InvalidDict', 'UserDict']:
        collectionHandler.create_index(
            [('word', 1)], unique=True, background=True)

    # try:
    # print('data2insert',data2insert)
    # 将所有 错误 异常 判断，交给上级 调用函数
    try:
        print('data2insert----',data2insert)
        result = collectionHandler.insert_many(data2insert, ordered=False)
        # print(result.inserted_ids)
        # 成功: 返回插入的数据行数
        return len(result.inserted_ids)
    except:
        raise



async def update_one(dbName, collectionName, queryDict={}, setDict={}):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    # 所有异常交给上面
    try:
        result1 = collectionHandler.update_one(queryDict, setDict)
        return (result1.modified_count)
    except:
        raise
    #    # modified_count 返回更新的条数
    #    # print(result1.modified_count)
    #    return (result1.modified_count)
    #except pymongo.errors.DuplicateKeyError as e:
    #    # print('error:',e)
    #    return ('duplicateError-projectName')
    #except Exception as e:
    #    # print('error:',e)
    #    return ('project-unknownError')


async def update_many(dbName, collectionName, queryDict={}, setDict={}):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result1 = collectionHandler.update_many(queryDict, setDict)
        # modified_count 返回更新的条数
        return (result1.modified_count)
    except:
        raise


async def copy_database(sourceDb, destDb):
    # 复制一个数据库， 该特性已经被 deprecated ，小心
    try:
        result = client.admin.command('copydb', fromdb=sourceDb, todb=destDb)
        # print('result',result)
        return (result)
        # result可能看起来这个样子
        # {'note': 'Support for the copydb command has been deprecated. See http://dochub.mongodb.org/core/copydb-clone-deprecation', 'ok': 1.0}
    except Exception as e:
        return 'copyDb-error'


async def drop_database(db2drop):
    try:
        result1 = client.drop_database(db2drop)
        return result1
    except:
        return 'error'


async def delete_one(dbName, collectionName, queryDict={}):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result1 = collectionHandler.delete_one(queryDict)
    except:
        raise
    else:
        return result1.deleted_count


async def delete_many(dbName, collectionName, queryDict):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result1 = collectionHandler.delete_many(queryDict)
        return result1.deleted_count
    except:
        return 'error'


async def check_collection_count(dbName, collectionName):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    return collectionHandler.count()
