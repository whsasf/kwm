"""
    定义几个 自定义的 异常
"""

class AccountNotExistError(Exception):
    # 账号未注册
    def __init__(self,msg):
        self.msg = msg
    # 异常描述信息
    def __str__(self):
        return f'{self.msg}'

class PasswordMismatchError(Exception):
    # 账号密码错误
    def __init__(self,msg):
        self.msg = msg
    # 异常描述信息
    def __str__(self):
        return f'{self.msg}'
