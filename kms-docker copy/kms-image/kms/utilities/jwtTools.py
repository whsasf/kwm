import jwt
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import json 
from fastapi import HTTPException, Header,Depends

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)

# 验证jwt是否有效的装饰器

async def verify_token( authorization: str = Header("Authorization")):
    if len(authorization.split()) == 2:
        myjwt = authorization.split()[1]
        try:
            result = await verifyJWT(myjwt)
        except jwt.exceptions.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail='登录已过期,请重新登录')
        except Exception as e:
            raise HTTPException(status_code=401, detail='验证错误,请重新登录')
        else:
            return
    else:
        raise HTTPException(status_code=401, detail='验证错误,请重新登录')

# 请求会向 dic 里面插入 'data' 字段, 内容为用户姓名

async def createJWT(newdata):
    secretKey = 'd261ea8ca4efb56c04f4d52333b217e515ea98718ef030e3e4d040dfdc8ec889'
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    payload = {
        'exp': utc_now.astimezone(SHA_TZ) + timedelta(hours=1),  # jwt过期时间1小时
        'iat': utc_now.astimezone(SHA_TZ),
        'iss': 'dianbaobao',  # 签名
    } 

    payload['data'] = newdata
    token = jwt.encode(payload, secretKey, algorithm='HS256')
    #print(token)
    return (token)


async def verifyJWT(payload):
    secretKey = 'd261ea8ca4efb56c04f4d52333b217e515ea98718ef030e3e4d040dfdc8ec889'
    try:
        jwt.decode(payload, secretKey, issuer='dianbaobao', algorithms=['HS256'])
    except:
        raise
