from fastapi import APIRouter, HTTPException, Path, Depends, Query
from pydantic import BaseModel
import json
import pymongo
from bson import json_util
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import createnewproject, fetchAllProjects, updateProject, fetchAllProjects, deleteProject
from utilities.jwtTools import verify_token

router = APIRouter()
dbPrefix = 'KWM'


class Category(BaseModel):
    categoryName: str = Query(None, min_length=1, max_length=250)


class Project(BaseModel):
    # create_project 请求body数据模型
    projectName: str = Query(..., min_length=1, max_length=250)
    creater: str = Query(...,min_length=1, max_length=250)
    categories: Optional[List[Category]] = None


class UpdateProjectInfo(BaseModel):
    # update_project body数据模型
    projectName: str = Query(..., min_length=1, max_length=250)


class UpdateCategoryInfo(BaseModel):
    # UpdateCategory body数据模型
    categoryName: str = Query(..., min_length=1, max_length=250)


class CreateCategoryInfo(BaseModel):
    # createCategory body数据模型
    categoryName: str = Query(..., min_length=1, max_length=250)


@router.post("/", dependencies=[Depends(verify_token)],tags=["Projects"])
async def create_project(project: Project, currentPage: int = 1, pageSize: int = 10):
    # 操作流程:
    # 1. 插入时间戳
    # 2: 将项目名称 写入 keywordsManagement ->Project 表
    # 3: 将项目对应分类列表写入 项目名 -> Categories 表
    # 应该返回全部的 projects-> categories 对象
    # [{projectname: 'xx',creater: '', timestamp: '',categories:[1,2,3]},{},{}]
    # print(currentPage, pageSize)
    # 1 插入时间戳
    projectnew = project.dict()
    projectnew['timestamp'] = time.strftime(
        "%Y/%m/%d %H:%M:%S", time.localtime())  # getBJTime()
    # print('projectsnew',projectnew)
    # 2 写入数据库，并捕获所有的 异常
    try:
        result = await createnewproject(dbPrefix, 'Project', projectnew, currentpage=currentPage, pagesize=pageSize)
    except pymongo.errors.DuplicateKeyError as e:
        #print('重复错误！')
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'以下项目出现重复,创建失败! 项目名称: \'{errMsg}\'')
    except Exception as e:
        #print('其他错误')
        raise HTTPException(status_code=503, detail=e.details)
    else:
        # 返回正常值
        return (result)


@router.get("/", dependencies=[Depends(verify_token)],tags=["Projects"])
async def fetch_project(currentPage: int = 1, pageSize: int = 10):
    # -返回 所有项目数据
    #print(currentPage, pageSize)
    result = await fetchAllProjects(currentpage=currentPage, pagesize=pageSize)
    # print('get project:',result)
    return (result)


@router.patch("/{projectId}", dependencies=[Depends(verify_token)],tags=["Projects"])
async def update_project(*, projectId: str = Path(...), currentPage: int = 1, pageSize: int = 10, updateProjectInfo: UpdateProjectInfo):
    # 修改 项目名称，同时会触发修改 项目对应的 数据库的名称修改
    # print('projectId',projectId,updateProjectInfo.dict())
    try:
        oid = ObjectId(projectId)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        queryDict = {'_id': oid}
    setDict = updateProjectInfo.dict()
    # oldProjectName = setDict.pop('oldprojectName')
    # newProjectName = setDict['projectName']
    setDict = {"$set": setDict}
    try:
        result = await updateProject(dbPrefix, 'Project', queryDict = queryDict, setDict = setDict,currentPage=currentPage, pageSize=pageSize)
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'新项目名重复，修改失败! 冲突项目名称: \'{errMsg}\'')
    except Exception as e:
        #print('其他错误')
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result)


@router.delete("/{projectId}", dependencies=[Depends(verify_token)],tags=["Projects"])
async def delete_project(*, projectId: str = Path(...),currentPage: int = 1, pageSize: int = 10):
    # 删除项目:
    # print('projectId',projectId)
    try:
        oid = ObjectId(projectId)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        queryDict = {'_id': oid}
    result = await deleteProject(dbPrefix, 'Project', queryDict=queryDict,currentPage=currentPage,pageSize=pageSize)
    return (result)
