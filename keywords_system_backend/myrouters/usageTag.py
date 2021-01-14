from fastapi import APIRouter, HTTPException, Path, Query,Depends
from pydantic import BaseModel
import json
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from urllib.parse import unquote
from bson import json_util
from database.db_advanced import fetchUsageTags, findProjectIdFromProjectName
from utilities.jwtTools import verify_token
from collections import Counter


router = APIRouter()
dbPrefix = 'KWM'


@router.get("/{projectName}",dependencies=[Depends(verify_token)],tags=["UsageTag"])
async def getUsageTags(projectName: str):
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix, 'Project', queryDict={'projectName': projectName}, showDict={'_id': 1})
    if not projectId:
        raise HTTPException(status_code=503, detail='projectNotExist')
    #print('projectId',projectId)
    usageTags = await fetchUsageTags(dbPrefix+'-'+projectId,'extendedWords')
    datas = json.loads(usageTags)
    data = []
    rt = []
    for i in datas:
        if i.get('usageTag'):
            data+=i['usageTag']
    for j in Counter(data).most_common():
        rt.append({'name':str(j[0]), 'value':str(j[1])})
    return rt