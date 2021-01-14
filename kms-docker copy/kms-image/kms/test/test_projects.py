import pytest
from fastapi.testclient import TestClient

# 将路径加入 path
import os, sys
import pymongo
sys.path.append('.')

from ..main import app

client = TestClient(app)

testAccount = 'pytest@qq.com'
testAccountPassword = '7c4a8d09ca3762af61e59520943dc26494f8941b'
testAccountDepartment = '技术部'
jwtToken = ''


@pytest.fixture(scope='module')
def account():
    global testAccount, testAccountPassword,testAccountDepartment
    return testAccount,testAccountPassword,testAccountDepartment

@pytest.fixture(scope="class")
def CreatecAndClearAccount(account):
    # 创建账号
    payLoads = {'account': account[0],'shadow': account[1],'department':account[2]}
    response = client.post("/Account/Signup", json=payLoads)
    # 登录账号，获取 JWT
    payLoads = {'account': account[0],'shadow': account[1]}
    response = client.post("/Account/Signin", json=payLoads)
    global jwtToken # 获取jwt token
    jwtToken = response.json()['access_token']
    #print('jwtToken',jwtToken)
    
    # 执行最后，删除创建陈成功的账号
    yield
    MongoClient = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
    x = MongoClient['KWM']['User'].delete_one({'account': account[0]})

@pytest.mark.usefixtures('CreatecAndClearAccount')
class TestProjects:
    """
    测试项目相关的操作: 
    (1) 
    (2)
    (3)

    """