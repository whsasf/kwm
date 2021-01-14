from typing import Optional
from fastapi import FastAPI, Path
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from myrouters import projects,categories,account,urls,stopDict, Articles,invalidDict,userDict,basicWords,extendedWords,usageTag
from database.db_advanced import dbinit
from config import settings

import uvicorn

app = FastAPI()

# 允许的跨域来源
origins = settings.origins

# CSRF攻击防范
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 设定静态目录
app.mount("/static", StaticFiles(directory="static"), name="static")


# 引入子路由
app.include_router(account.router, prefix="/Account")
app.include_router(projects.router, prefix="/Projects")
app.include_router(categories.router, prefix="/Categories")
app.include_router(urls.router, prefix="/Urls")
app.include_router(Articles.router, prefix='/Articles')
app.include_router(basicWords.router, prefix="/basicWords")
app.include_router(extendedWords.router, prefix="/extendedWords")
app.include_router(stopDict.router, prefix='/StopDict')
app.include_router(invalidDict.router, prefix='/InvalidDict')
app.include_router(userDict.router, prefix='/UserDict')
app.include_router(usageTag.router, prefix='/UsageTag')


# 得到 index.html 的 文件句柄，应对SPA刷新页面后，浏览器发起的无效请求
with open('static/index.html','r',encoding='utf-8') as f:
        index = f.read()

@app.get("/",response_class=HTMLResponse,tags=["static"])
def read_root():
    return HTMLResponse(content=index, status_code=200)

@app.get("/favicon.ico",tags=["static"])
def read_favicon():
    return FileResponse(path='static/favicon.ico')


@app.get("/{xx:path}",tags=["static"])  # here  "/{xx:path}" match any path
def read_restAll():
    return HTMLResponse(content=index, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000, log_level="debug", reload=True)