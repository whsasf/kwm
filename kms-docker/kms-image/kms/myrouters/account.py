from fastapi import APIRouter, HTTPException, Path,Query, Depends
from pydantic import BaseModel
import json
import pymongo
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import handleSignup, handleSignin, fetchUsers
from myExceptions import AccountNotExistError, PasswordMismatchError
from utilities.jwtTools import verify_token

router = APIRouter()
dbPrefix = 'KWM'

class SignInAccountInfo(BaseModel):
    account: str = Query(...,min_length=1,max_length=250) #  Query(None, min_length=3, max_length=50)
    shadow: str =  Query(...,min_length=1,max_length=100)

class AccountInfo(BaseModel):
    account: str = Query(...,min_length=1,max_length=250)
    shadow: str = Query(...,min_length=1,max_length=100)
    department: str = Query(...,min_length=1,max_length=100)



@router.post("/Signup",tags=["Account"])
async def Signup(accountinfo:AccountInfo):
    try:
        result = await handleSignup(dbPrefix, 'User', accountinfo.dict())
    except pymongo.errors.DuplicateKeyError as e:
        raise HTTPException(status_code=402, detail='该用户已经注册!')
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.details)
    else:
        return ({'detail': '注册成功!'})



@router.post("/Signin",tags=["Account"])
async def Signin(signInAccountInfo:SignInAccountInfo):
    #print(signInAccountInfo.dict())
    #处理用户登录
    try:
        result = await handleSignin(dbPrefix, 'User', signInAccountInfo.dict())
    except AccountNotExistError as e:
        raise HTTPException(status_code=503, detail='账号未注册!')
    except PasswordMismatchError as e:
        raise HTTPException(status_code=503, detail='账号密码不对!')
    except Exception as e:
        raise HTTPException(status_code=503, detail='其他错误!')
    else:
        return (result)


@router.post("/Signout",tags=["Account"])
async def Signout():
    #处理用户登录
    pass


@router.get("/AllUsers",dependencies=[Depends(verify_token)],tags=["Account"])
async def all_users():
    users = await fetchUsers(dbPrefix, 'User',showDict={'_id':0, 'account':1})
    #print('users',users)
    return users
