import configparser
import json
import re
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector as mydb

from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from webxray.PhantomDriver import PhantomDriver
from webxray.ParseURI import ParseURI
from webxray.MySQLDriver import MySQLDriver

from consts import BEHAVIOR_LOG_QUERT, CLICK_DOC_LOG_QUERY, CLICK_HISTORY_LOG_QUERY
from request_models import (
    BehaviorLoggingRequest,
    CipherTestRequest,
    DocumentLoggingRequest,
    HistoryLoggingRequest,
    XrayAnalyseRequest,
)
from utils import decrypt, history_filter, unpadPKCS7

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            (
                request.uid,
                request.timeOnPage,
                request.currentPage,
                request.positionOnPage,
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
                request.uid,
                request.timeOnPage,
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
                request.uid,
                request.timeOnPage,
                request.linkedDocumentUrl,
                request.linkedPageNum,
                request.collapse,
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


@app.post("/api/wbxr/analyze")
async def post_analyze_url(request: XrayAnalyseRequest):
    print('Data recieve.')
    status = False
    cookies = []

    driver = MySQLDriver('wbxr_gayatri')
    try:
        url = unpadPKCS7(decrypt(request.url))
        url = url.decode('utf8')
        print('Encoded', url)

        if history_filter(url):
            driver.db.execute(
                "SELECT cookie.`domain` "
                "FROM page "
                "LEFT JOIN page_cookie_junction "
                "ON page.id = page_cookie_junction.page_id "
                "LEFT JOIN cookie "
                "ON page_cookie_junction.cookie_id = cookie.id "
                "WHERE page.start_uri_md5 = MD5(%s)",
                (url,),
            )
            fetched = driver.db.fetchall()
            if fetched:
                cookies = fetched
            else:
                cookies = analyze_url(url)
        else:
            cookies = []
        print(cookies)
    except Exception as e:
        print(e)
    else:
        status = True

    return JSONResponse(content={"status": status, "cookies": cookies})


def analyze_url(uri: str) -> List[str]:
    """
    Analyze given URI and get page information by using webXray.
    Arg:
        uri(str): Any URI that is not analyzed yet.
    Return:
        dict {"uri": list[str]}: (key: given uri, value: listed domain name of cookies)
    """
    parser = ParseURI()

    pd = PhantomDriver("--ignore-ssl-errors=true --ssl-protocol=any", "wbxr_logger.js")
    output = pd.execute(uri, 25)

    if re.match("^FAIL.+", output):
        # Probably this isn't needed
        return []
    else:
        try:
            parsed_data = json.loads(re.search("(\{.+\})", output).group(1))
        except Exception as e:
            print(e)
            return []

        orig_domain = parser.get_domain_pubsuffix_tld(uri)[0]
        cookie_domains = map(lambda x: x["domain"], parsed_data["cookies"])
        tpcookie_domains = filter(
            lambda x: parser.get_domain_pubsuffix_tld(f"http://{x[1:]}")[0]
            != orig_domain,
            cookie_domains,
        )
        tpcookie_domain_names = map(remove_dot, tpcookie_domains)
        return list(tpcookie_domain_names)


def remove_dot(s: str) -> str:
    if s.startswith("."):
        return s.lstrip(".")
    else:
        return s


@app.post("/cipher")
def cipher_test(request: CipherTestRequest):
    try:
        print(unpadPKCS7(decrypt(request.text)))
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500)
    else:
        return JSONResponse(status_code=200)
