from fastapi import APIRouter, HTTPException, Path,Depends
from pydantic import BaseModel
import json
import pymongo
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import updateCategory, deleteCategory, createCategory, getCategories, findProjectIdFromProjectName
from utilities.jwtTools import verify_token


router = APIRouter()
dbPrefix = 'KWM'

class UpdateCategoryInfo(BaseModel):
    # UpdateCategory body数据模型
    categoryName: str


class CreateCategoryInfo(BaseModel):
    # createCategory body数据模型
    categoryName: str


@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["Categories"])
async def fetchCategories(*,projectName: str = Path(...)):
    # 查询Project Name下的所有 目录列表
    print(projectName)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    try:
        result = await getCategories(dbPrefix+'-'+projectId,'Categories')
        #print('cccc',result)
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result)


@router.patch("/{projectId}/{categoryId}",dependencies=[Depends(verify_token)],tags=["Categories"])
async def update_category(*,projectId,categoryId: str = Path(...), currentPage: int = 1, pageSize: int = 10, updateCategoryInfo: UpdateCategoryInfo):
    # 修改特定数据库中的分类
    # print(projectName,categoryId,updateCategoryInfo.dict())
    try:
        oid = ObjectId(categoryId)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        queryDict = {'_id': oid}
    setDict = updateCategoryInfo.dict()
    setDict = {"$set": setDict}
    try:
        result = await updateCategory(dbPrefix + '-' + projectId, 'Categories', queryDict=queryDict, setDict=setDict, currentPage=currentPage, pageSize=pageSize)
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'新目录名重复，修改失败! 冲突目录名称: \'{errMsg}\'')
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result)


@router.delete("/{projectId}/{categoryId}",dependencies=[Depends(verify_token)],tags=["Categories"])
async def delete_category(*,projectId,categoryId: str = Path(...),currentPage: int = 1, pageSize: int = 10):
    # 删除特定项目中的特定目录: 
    # print(projectName,categoryId)
    try:
        oid = ObjectId(categoryId)
    except:
        raise HTTPException(status_code=503, detail='invalid ObjectID')
    else:
        queryDict = {'_id': oid}
    try:
        result = await deleteCategory(dbPrefix+'-'+projectId,'Categories',queryDict=queryDict,currentPage=currentPage,pageSize=pageSize)
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result)


@router.post("/{projectId}",dependencies=[Depends(verify_token)],tags=["Categories"])
async def create_category(*,projectId: str = Path(...),currentPage: int = 1, pageSize: int = 10,createCategoryInfo:CreateCategoryInfo):
    # 特定项目中，添加特定目录: 
    # print(projectName,createCategoryInfo.dict())
    setDict = createCategoryInfo.dict()
    try:
        result = await createCategory(dbPrefix + '-' + projectId, 'Categories', setDict = setDict,currentPage=currentPage,pageSize=pageSize )
    except pymongo.errors.DuplicateKeyError as e:
        errMsg = e.details['errmsg'].split(':')[-1].strip('}').strip().strip('"')
        #print('errMsg',errMsg)
        raise HTTPException(status_code=503, detail=f'新目录名重复，创建失败! 冲突目录名称: \'{errMsg}\'')
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return (result)