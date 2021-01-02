import configparser
from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector as mydb

from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserLoggingRequest(BaseModel):
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
        password=_parser["mysql"]["password"],
        database=_parser["mysql"]["database"]
    )

@app.post('/storelog')
async def post_user_log(request: UserLoggingRequest):
    """
    Recieve User log object, return status.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    status = False

    try:
        cursor.execute('INSERT INTO logs VALUES(%s, %s, %s, %s, %s)', (request.id, request.uid, request.timeOnPage, request.pageUrl, request.linkedPageNum))
    except Exception as e:
        print(e)
        status = False
    else: 
        status = True
        cursor.commit()
    finally:
        cursor.close()
        connection.close()

    return JSONResponse(content={'status': status})

@app.post('/ping')
async def ping_pong(request: BaseModel):
    return request 
