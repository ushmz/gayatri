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


BEHAVIOR_LOG_QUERT = (
    "INSERT INTO behavior_log(ext_id, time_on_page, position_on_page)"
    "VALUES(%s, %s, %s)"
)


CLICK_DOC_LOG_QUERY = (
    "INSERT INTO click_log_doc(ext_id, page_url, linked_page_num)" "VALUES(%s, %s, %s)"
)


CLICK_HISTORY_LOG_QUERY = (
    "INSERT INTO click_log_history(ext_id, linked_doc_url, linked_page_num)"
    "VALUES(%s, %s, %s)"
)


class BehaviorLoggingRequest(BaseModel):
    id: str
    timeOnPage: int
    positionOnPage: int

    def queryalize(self) -> str:
        return BEHAVIOR_LOG_QUERT.format(self.id, self.timeOnPage, self.positionOnPage)


class DocumentLoggingRequest(BaseModel):
    id: str
    pageUrl: str
    linkedPageNum: int

    def queryalize(self) -> str:
        return CLICK_DOC_LOG_QUERY.format(self.id, self.pageUrl, self.linkedPageNum)


class HistoryLoggingRequest(BaseModel):
    id: str
    linkedDocumentUrl: str
    linkedPageNum: int

    def queryalize(self) -> str:
        return CLICK_HISTORY_LOG_QUERY.format(
            self.id, self.linkedDocumentUrl, self.linkedPageNum
        )


def get_db_connection():
    _parser = configparser.ConfigParser()
    _parser.read("./config.ini")

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
            BEHAVIOR_LOG_QUERT,
            (request.id, request.timeOnPage, request.positionOnPage),
        )
    except Exception as e:
        print(e)
        status = False
    else:
        connection.commit()
        status = True
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
            CLICK_DOC_LOG_QUERY,
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
        connection.commit()
        status = True
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
            CLICK_HISTORY_LOG_QUERY,
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
        connection.commit()
        status = True
    finally:
        cursor.close()
        connection.close()

    return JSONResponse(content={"status": status})


@app.post("/ping")
async def ping_pong(request: BaseModel):
    return request
