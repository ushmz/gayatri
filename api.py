import configparser
from enum import unique
import json
from fastapi import FastAPI
import re
import urllib.parse
from typing import Any, Union

# from webXray.webxray import Collector
from webxray.MySQLDriver import MySQLDriver
from webxray.OutputStore import OutputStore
from webxray.PhantomDriver import PhantomDriver

app = FastAPI()

config = configparser.ConfigParser()
config.read('config.ini')

EXTENTION_ID = config['DEFAULT']['extension_id']

# ?
def after_request(response):
    #response.headers.add('Access-Control-Allow-Origin', f'chrome-extension://{EXTENTION_ID}')
    response.headers.add('Access-Control-Allow-Origin', 'https://www.google.com')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'append,delete,entries,foreach,get,has,keys,set,values,Authorization')
    response.headers.add('Access-Control-Allow-Headers', "X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept")
    return response

def uri_filter(uri: str) -> bool:
    """
    It is implied that this method is passed to `filter`.  

    Arg:
        uri(str): uri
    Return:
        (bool): Keep given uri in list or not
    """
    # drop trailing '/, clean off white space, make lower, create cli-safe uri
    # with parse.quote, but exclude :/ b/c of http://
    uri = re.sub('/$', '', urllib.parse.quote(uri.strip(), safe=":/").lower())

    # if it is a m$ office or other doc, skip
    if re.match('.+(pdf|ppt|pptx|doc|docx|txt|rtf|xls|xlsx)$', uri):
        return False
    return True


def get_cookie_domain(db: Any, uri: str) -> dict:
    """
    Check Stored data. If given uri is exist in stored data, return cookie list contained in given uri.
    If not, analyze uri and return result.
    Args:
        uri(str): Any URI
    Return:
        (dict {"uri": list[str]}): (key: given uri, value: listed domain name of cookies)
    """
    db.execute("SELECT cookie.`domain` FROM page LEFT JOIN page_cookie_junction ON page.id = page_cookie_junction.page_id LEFT JOIN cookie ON page_cookie_junction.cookie_id = cookie.id WHERE page.start_uri_md5 = MD5(%s)", (uri,))
    if db.fetchall():
        "TODO: Format database output"
        return {uri: db.fetchall()} 
    else:
        return analyze_url(uri)
        
def analyze_url(uri: str) -> dict:
    """
    Analyze given URI and get page information by using webXray.
    Arg:
        uri(str): Any URI that is not analyzed yet.
    Return:
        (dict {"uri": list[str]}): (key: given uri, value: listed domain name of cookies)
    """
    db_name = 'wbxr_gayatri'
    output_store = OutputStore(db_name)

    pd = PhantomDriver('--ignore-ssl-errors=true --ssl-protocol=any', 'wbxr_logger.js') 
    output = pd.execute(uri, 25)

    if re.match('^FAIL.+', output):
        # Probably this isn't needed
        resp = {
            'status': False,
            'message': output
        }
    else:
        "TODO: Get cookie domain array from output"
        status = output_store.store(uri, output)
        resp = {
            'status': True,
            'message': status
        }
    return resp

# @app.route('/analyze', methods=["POST"])
def postURI(request):
    db_name = 'wbxr_gayatri'
    sql_driver = MySQLDriver(db_name)

    # Recieve request body
    user_histories = request.data['histories']
    uri_process = list(filter(uri_filter, user_histories))
    # Return this as a HTTP response
    response = [ get_cookie_domain(sql_driver, uri) for uri in uri_process]
    

resp = analyze_url('https://qiita.com/pipi0813/items/1a940f4452e28345c031')
print(resp)