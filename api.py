import configparser
from typing import Union
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
    allow_headers=["*"],
)


class BehaviorLoggingRequest(BaseModel):
    id: str
    timeOnPage: int
    positionOnPage: int

    def queryalize(self):
        return "INSERT INTO table_name VALUES({}, {}, {})".format(
            self.id, self.timeOnPage, self.positionOnPage
        )


class DocumentLoggingRequest(BaseModel):
    id: str
    pageUrl: str
    linkedPageNum: int

    def queryalize(self):
        return "INSERT INTO table_name VALUES({}, {}, {})".format(
            self.id, self.pageUrl, self.linkedPageNum
        )


class HistoryLoggingRequest(BaseModel):
    id: str
    linkedDocumentUrl: str
    linkedPageNum: int

    def queryalize(self):
        return "INSERT INTO table_name VALUES({}, {}, {})".format(
            self.id, self.linkedDocumentUrl, self.linkedPageNum
        )


def get_db_connection():
    _parser = configparser.ConfigParser()
    _parser.read("./mysql.ini")

    return mydb.connect(
        host=_parser["mysql"]["host"],
        port=_parser["mysql"]["port"],
        user=_parser["mysql"]["user"],
        password=_parser["mysql"]["password"],
        database=_parser["mysql"]["database"],
    )


@app.post("/printlog")
async def print_user_log(
    request: Union[
        BehaviorLoggingRequest, DocumentLoggingRequest, HistoryLoggingRequest
    ]
):
    """
    Recieve User log object, return status.
    """
    print(request.queryalize())

    return JSONResponse(content={"status": True, "query": request.queryalize()})


@app.post("/api/logs/behavior")
async def post_behavior_logs(request: BehaviorLoggingRequest):
    """
    Recieve User log object, return status.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    status = False

    try:
        cursor.execute(
            "INSERT INTO logs VALUES(%s, %s, %s)",
            (request.id, request.timeOnPage, request.positionOnPage),
        )
    except Exception as e:
        print(e)
        status = False
    else:
        status = True
        cursor.commit()
    finally:
        cursor.close()
        connection.close()

    return JSONResponse(content={"status": status})


@app.post("/api/logs/click/docs")
async def post_documents_log(request: DocumentLoggingRequest):
    """
    Recieve User log object, return status.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    status = False

    try:
        cursor.execute(
            "INSERT INTO logs VALUES(%s, %s, %s)",
            (
                request.id,
                request.pageUrl,
                request.linkedPageNum,
            ),
        )
    except Exception as e:
        print(e)
        status = False
    else:
        status = True
        cursor.commit()
    finally:
        cursor.close()
        connection.close()

    return JSONResponse(content={"status": status})


@app.post("/api/logs/click/hstr")
async def post_history_log(request: HistoryLoggingRequest):
    """
    Recieve User log object, return status.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    status = False

    try:
        cursor.execute(
            "INSERT INTO logs VALUES(%s, %s, %s)",
            (
                request.id,
                request.linkedDocumentUrl,
                request.linkedPageNum,
            ),
        )
    except Exception as e:
        print(e)
        status = False
    else:
        status = True
        cursor.commit()
    finally:
        cursor.close()
        connection.close()

    return JSONResponse(content={"status": status})


@app.post("/ping")
async def ping_pong(request: BaseModel):
    return request
