import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel
import time
import re
import urllib.parse
from typing import Any, List, Optional

from starlette.responses import JSONResponse 

# from webXray.webxray import Collector
from webxray.MySQLDriver import MySQLDriver
from webxray.OutputStore import OutputStore
from webxray.PhantomDriver import PhantomDriver
from webxray.ParseURI import ParseURI

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

@app.middleware('http')
async def add_cors_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    # if ext_id: response.headers['Access-Control-Allow-Origin'] = f'"chrome-extension://{ext_id}/"'
    # response.headers['Access-Control-Allow-Methods'] = '"post"'
    # response.headers['Access-Control-Allow-Headers'] = '"X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept"'
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

def history_filter(histry: BrowserHistory) -> bool:
    """
    It is implied that this method is passed to `filter`.  

    Arg:
        uri(str): uri
    Return:
        (bool): Keep given uri in list or not
    """
    url = histry.url
    # drop trailing '/, clean off white space, make lower, create cli-safe uri
    # with parse.quote, but exclude :/ b/c of http://
    url = re.sub('/$', '', urllib.parse.quote(url.strip(), safe=":/").lower())

    # if it is a m$ office or other doc, skip
    # TODO: Other file extensions
    if re.match('.+(pdf|ppt|pptx|doc|docx|txt|rtf|xls|xlsx)$', url):
        return False
    return True


def get_cookie_domain(db: Any, uri: str) -> list:
    """
    Check Stored data. If given uri is exist in stored data, return cookie list contained in given uri.
    If not, analyze uri and return result.
    DB query return...
    - 0 rows -> Given URL page is not stored in DB
    - 1 row but null -> Given URL page has no 3rd-party cookie
    - More than 0 row -> Given URL page has 3rd-party cookie(s)

    Args:
        uri(str): Any URI
    Return:
        (list[str]): listed domain name of cookies
    """
    db.execute("SELECT cookie.`domain` FROM page LEFT JOIN page_cookie_junction ON page.id = page_cookie_junction.page_id LEFT JOIN cookie ON page_cookie_junction.cookie_id = cookie.id WHERE page.start_uri_md5 = MD5(%s)", (uri,))
    fetched = db.fetchall()
    if fetched:
        "TODO: Format database output"
        return fetched
    else:
        return analyze_url(uri)
        
def analyze_url(uri: str) -> list:
    """
    Analyze given URI and get page information by using webXray.
    Arg:
        uri(str): Any URI that is not analyzed yet.
    Return:
        (dict {"uri": list[str]}): (key: given uri, value: listed domain name of cookies)
    """
    db_name = 'wbxr_gayatri'
    output_store = OutputStore(db_name)
    uri_parser = ParseURI()

    pd = PhantomDriver('--ignore-ssl-errors=true --ssl-protocol=any', 'wbxr_logger.js') 
    output = pd.execute(uri, 25)

    if re.match('^FAIL.+', output):
        # Probably this isn't needed
        resp = {
            'status': False,
            'message': output
        }
        return []
    else:
        try:
            parsed_data = json.loads(re.search('(\{.+\})', output).group(1))
        except Exception as e:
            return []

        status = output_store.store(uri, output)

        orig_domain = uri_parser.get_domain_pubsuffix_tld(uri)[0]
        cookie_domains = map(lambda x:x['domain'], parsed_data['cookies'])
        tpcookie_domains = filter(lambda x:uri_parser.get_domain_pubsuffix_tld(f'http://{x[1:]}')[0] != orig_domain, cookie_domains)
        return list(tpcookie_domains)

# @app_router.post('/analyze')
@app.post('/analyze')
async def post_uri(request: HistoryRequestBody):
    print('Recieve request...')
    db_name = 'wbxr_gayatri'
    sql_driver = MySQLDriver(db_name)

    # Recieve request body
    user_histories = request.data
    print('Filtering URLs...', end=' ')
    history_process = list(filter(history_filter, user_histories))
    print('DONE')

    # Return this as a HTTP response
    print('processing URL...', end=' ')
    histories = [{
        'title': hstr.title,
        'url': hstr.url,
        'cookies': get_cookie_domain(sql_driver.db, hstr.url)
    } for hstr in history_process]
    response = JSONResponse(histories) 
    print('DONE. Return')
    response.headers['Access-Control-Allow-Origin'] = f'"chrome-extension://{request.ext_id}/"'
    response.headers['Access-Control-Allow-Methods'] = '"post"'
    response.headers['Access-Control-Allow-Headers'] = '"X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept"'
    return response 

# @app_router.post('/ping')
@app.post('/ping')
async def ping_pong(request: ExtensionBaseRequest):
    ext_id = request.ext_id
    request_json = request.json()
    response = JSONResponse(request_json)
    response.headers['Access-Control-Allow-Origin'] = f'"chrome-extension://{ext_id}/"'
    response.headers['Access-Control-Allow-Methods'] = '"post"'
    response.headers['Access-Control-Allow-Headers'] = '"X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept"'
    return response 

# app.include_router(app_router, dependencies=[Depends(add_cors_header)])