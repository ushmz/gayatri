import json
import configparser
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel
import time
from typing import Any, Dict, List, Optional, Union, final
import mysql.connector as mydb

from starlette.responses import JSONResponse 

app = FastAPI()
# app_router = APIRouter()

class BrowserHistory(BaseModel):
    id: Optional[str] = ''
    lastVisitTime: Optional[float] = 0.
    title: str
    typedCount: Optional[int] = 0
    url: str
    visitCount: Optional[int] = 0

class ExtensionBaseRequest(BaseModel): 
    ext_id: str

class HistoryRequestBody(ExtensionBaseRequest):
    data: List[BrowserHistory]
    description: Optional[str] = ''
    def jsonize(self): return {"data": self.data, "description": self.description, "ext_id": self.ext_id}

class UserLoggingRequest(ExtensionBaseRequest):
    id: str
    uid: str
    timeOnPage: int
    pageUrl: str
    linkedPageNum: int

def get_db_connection():
    _parser = configparser.ConfigParser()
    _parser.read("./mysql.ini")

    return mydb.connect(
        host=_parser["mysql"]["host"],
        port=_parser["mysql"]["port"],
        user=_parser["mysql"]["user"],
        password=_parser["mysql"]["passwd"],
        database=_parser["mysql"]["db"]
    )

@app.post('/storelog')
async def post_user_log(request: UserLoggingRequest):
    """
    Recieve User log object, return status.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('INSERT INTO logs VALUES(%s, %s, %s, %s, %s)', (request.id, request.uid, request.timeOnPage, request.pageUrl, request.linkedPageNum))
    except Exception as e:
        print(e)
        status = False
    else: 
        cursor.commit()
        status = True
    finally:
        cursor.close()
        connection.close()

    return {'status': status}

@app.middleware('http')
async def add_cors_header(request: Request, call_next):
    """
    In middleware, it seems to block application to execute `await request.json()` or something read request.
    """
    start_time = time.time()
    response = await call_next(request)
    # if ext_id: response.headers['Access-Control-Allow-Origin'] = f'"chrome-extension://{ext_id}/"'
    # response.headers['Access-Control-Allow-Methods'] = '"post"'
    # response.headers['Access-Control-Allow-Headers'] = '"X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept"'
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

def add_cors_header(response: JSONResponse, ext_id: str):
    response.headers['Access-Control-Allow-Origin'] = f'chrome-extension://{ext_id}'
    response.headers['Vary'] = 'Origin'
    response.headers['Access-Control-Allow-Methods'] = 'post'
    response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept'
    return response

# @app_router.post('/ping')
@app.post('/ping')
async def ping_pong(request: ExtensionBaseRequest):
    ext_id = request.ext_id
    request_json = request.json()
    response = JSONResponse(request_json)
    response.headers['Access-Control-Allow-Origin'] = f'chrome-extension://{ext_id}'
    response.headers['Vary'] = 'Origin'
    response.headers['Access-Control-Allow-Methods'] = 'post'
    response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept'
    return response 

# app.include_router(app_router, dependencies=[Depends(add_cors_header)])