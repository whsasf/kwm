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
    global testAccount
    return testAccount

@pytest.fixture(scope="class")
def clearAccount(account):
    # 执行最后，删除创建陈成功的账号
    yield
    MongoClient = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
    x = MongoClient['KWM']['User'].delete_one({'account': account})

@pytest.mark.usefixtures('clearAccount')
class TestAccount:
    """
    测试账号相关的操作: 

    1: 正常功能测试
    (1) 首次注册:成功
    (2) 再次相同账号注册: 失败，并返回失败原因
    (3) 登录成功
    (4) 登录失败: 并告知原因是 账号错误
    (5) 登录失败: 并告知原因是 密码错误
    (6) 获取所有账号信息: 成功

    2: 参数 测试
    (1) 注册信息，仅包含账户，应该失败
    (2) 注册信息，仅包含密码，应该失败
    (3) 注册信息，仅包含部门，应该失败

    (4) 注册信息，密码空，应该失败
    (5) 注册信息，账号空，应该失败
    (6) 注册信息，部门空，应该失败

    (7) 注册信息，密码长度大于100，应该失败
    (8) 注册信息，部门长度大于100，应该失败
    (9) 注册信息，账号长度大于250，应该失败
    
    (10) 登录信息，仅包含账户，应该失败
    (11) 登录信息，仅包含密码，应该失败

    (12) 登录信息，密码空，应该失败
    (13) 登录信息，账号空，应该失败

    (14) 登录信息，密码长度大于100，应该失败
    (15) 登录信息，账号长度大于250，应该失败

    """

    def test_signup_success(self):
        """
        注册新用户，应当成功
        """
        payLoads = {'account': testAccount,'shadow': testAccountPassword,'department':testAccountDepartment} # sha(123456) = 7c4a8d09ca3762af61e59520943dc26494f8941b
        response = client.post("/Account/Signup", json=payLoads)

        assert response.status_code == 200
        assert response.json()['detail']== '注册成功!'

    def test_signup_again_failed(self):
        """
        相同账号再次注册用户，应当失败
        """
        payLoads = {'account': testAccount,'shadow': testAccountPassword,'department':testAccountDepartment}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 402
        assert response.json()['detail'] == '该用户已经注册!'
        
    def test_signin_wrong_password_failed(self):
        """
        密码错误，应当失败
        """
        payLoads = {'account': testAccount,'shadow': 'wrongpassword'}
        response = client.post("/Account/Signin", json=payLoads)

        assert response.status_code == 503
        assert response.json()['detail'] == '账号密码不对!'
        
    def test_signin_not_existed_account_failed(self):
        """
        登录不存在的账号，应当失败
        """
        payLoads = {'account': 'notExistedAccount','shadow': testAccountPassword}
        response = client.post("/Account/Signin", json=payLoads)

        assert response.status_code == 503
        assert response.json()['detail'] == '账号未注册!'
    

    def test_signin_success(self):
        """
        用户名密码都正确，应当成功
        """
        payLoads = {'account': testAccount,'shadow': testAccountPassword}
        response = client.post("/Account/Signin", json=payLoads)
        global jwtToken # 获取jwt token
        jwtToken = response.json()['access_token']
        assert response.status_code == 200
        assert response.json()['username'] == testAccount

    
    def test_get_all_userInfo_success(self):
        """
        获取所有用户信息，应当成功，并返回用户信息. 此 api 包含 JWT header
        """
        response = client.get("/Account/AllUsers",headers={"authorization": "Bearer " + jwtToken})
        assert response.status_code == 200
        assert type(response.json()['count']) == int
        if response.json()['count'] > 0:
            # 如果存在 用户，那么用户名中应该 包含  @
            assert '@' in response.json()['content'][0]['account']

    def test_signup_only_with_account_failed(self):
        """
        注册信息，仅包含账户，应该失败
        """
        payLoads = {'account': testAccount}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422
    
    def test_signup_only_with_password_failed(self):
        """
        注册信息，仅包含密码，应该失败
        """
        payLoads = {'shadow': testAccountPassword}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422
    
    def test_signup_only_with_department_failed(self):
        """
        注册信息，仅包含部门信息，应该失败
        """
        payLoads = {'department':testAccountDepartment}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422
    
    def test_signup_with_empty_account_failed(self):
        """
        注册信息，账户为空，应该失败
        """
        payLoads = {'account': '','shadow': testAccountPassword,'department':testAccountDepartment}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422
    
    def test_signup_with_empty_password_failed(self):
        """
        注册信息，密码为空，应该失败
        """
        payLoads = {'account': testAccount,'shadow': '','department':testAccountDepartment}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422

    def test_signup_with_empty_department_failed(self):
        """
        注册信息，部门为空，应该失败
        """
        payLoads = {'account': testAccount,'shadow': testAccountPassword,'department':''}
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422

    def test_signup_account_length_greater_than_250_failed(self):
        """
        注册账号长度超过250，应当失败
        """
        payLoads = {'account': 'sdfsfsdnfslnfsklfnsldfnsdlfndslfkdslfkndslkfnsdlfkndsfoewihfewyf9shdfsdkfsdlfhsdlfsdlfhdslfhdsflsdfsldfhsdl87y87fdy832yer82y78qwydw8dywdy8qwq8wdyqw8dqwtd8qwtdqw8dtqwd8wqdfsofy23dwwdwdwdeyw89ryw9rywe9rw8eyr9ewyew9rywe9ryew9rwerw9e8rywe9ryew9r8ywe9rew9r', \
            'shadow': testAccountPassword,'department':testAccountDepartment} # 账号长度 251>250
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422

    def test_signup_password_length_greater_than_100_failed(self):
        """
        注册密码长度超过100，应当失败
        """
        payLoads = {'account': testAccount, 'shadow': 'sdfasdfasfasdasdasdasdasdasd23dwwdwdwdeyw89rw9rywe9rw8eyr9yew9rywe9ryew9rwerw9e8rywe9ryew9r8ywe9rew9r', \
            'department':testAccountDepartment} # 密码长度 101>100
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422
    
    def test_signup_department_length_greater_than_100_failed(self):
        """
        注册部门长度超过100，应当失败
        """
        payLoads = {'account': testAccount, 'shadow': testAccountPassword, \
            'department':'sdfasdfasfasdasdasdasdasdasd23dwwdwdwdeyw89rw9rywe9rw8eyr9yew9rywe9ryew9rwerw9e8rywe9ryew9r8ywe9rew9r'} # 部门长度 101>100
        response = client.post("/Account/Signup", json=payLoads)
        assert response.status_code == 422

    def test_signin_only_with_account_failed(self):
        """
        登录信息，仅包含账户，应该失败
        """
        payLoads = {'account': testAccount}
        response = client.post("/Account/Signin", json=payLoads)
        assert response.status_code == 422
    
    def test_signin_only_with_password_failed(self):
        """
        登录信息，仅包含密码，应该失败
        """
        payLoads = {'shadow': testAccountPassword}
        response = client.post("/Account/Signin", json=payLoads)
        assert response.status_code == 422
    
    def test_signin_with_empty_account_failed(self):
        """
        登录信息，账户为空，应该失败
        """
        payLoads = {'account': '','shadow': testAccountPassword}
        response = client.post("/Account/Signin", json=payLoads)
        assert response.status_code == 422
    
    def test_signin_with_empty_password_failed(self):
        """
        登录信息，密码为空，应该失败
        """
        payLoads = {'account': testAccount,'shadow': ''}
        response = client.post("/Account/Signin", json=payLoads)
        assert response.status_code == 422

    def test_signin_account_length_greater_than_250_failed(self):
        """
        登录账号长度超过250，应当失败
        """
        payLoads = {'account': 'sdfsfsdnfslnfsklfnsldfnsdlfndslfkdslfkndslkfnsdlfkndsfoewihfewyf9shdfsdkfsdlfhsdlfsdlfhdslfhdsflsdfsldfhsdl87y87fdy832yer82y78qwydw8dywdy8qwq8wdyqw8dqwtd8qwtdqw8dtqwd8wqdfsofy23dwwdwdwdeyw89ryw9rywe9rw8eyr9ewyew9rywe9ryew9rwerw9e8rywe9ryew9r8ywe9rew9r', \
            'shadow': testAccountPassword} # 账号长度 251>250
        response = client.post("/Account/Signin", json=payLoads)
        assert response.status_code == 422

    def test_signin_password_length_greater_than_100_failed(self):
        """
        登录密码长度超过100，应当失败
        """
        payLoads = {'account': testAccount, 'shadow': 'sdfasdfasfasdasdasdasdasdasd23dwwdwdwdeyw89rw9rywe9rw8eyr9yew9rywe9ryew9rwerw9e8rywe9ryew9r8ywe9rew9r'} # 密码长度 101>100
        response = client.post("/Account/Signin", json=payLoads)
        assert response.status_code == 422