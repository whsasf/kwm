from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    
    # 允许的跨域源设置
    origins:  List[str] = [
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:3000",
        "http://192.168.1.3:8080",
        "http://192.168.20.160:8080",
        "http://114.67.113.229:3000"
    ]


settings = Settings()
