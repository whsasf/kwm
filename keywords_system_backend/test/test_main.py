from fastapi.testclient import TestClient

# 将路径加入 path
import os, sys
sys.path.append('.')

from ..main import app

client = TestClient(app)

class TestMain:

    def test_read_main(self):
        """
        测试 访问'/'，应当返回index.html
        """
        response = client.get("/")
        assert response.status_code == 200


    def test_read_favicon(self):
        """
        测试 访问'/favicon.ico'，应当返回favicon.ico
        """
        response = client.get("/favicon.ico")
        assert response.status_code == 200


    def test_read_defaullt_route(self):
        """
        测试 默认路由
        """
        response = client.get("/{xx:path}")
        assert response.status_code == 200
