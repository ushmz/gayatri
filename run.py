from flask import Flask, Request, request, Response
import configparser
import json

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

EXTENTION_ID = config['DEFAULT']['extension_id']

@app.after_request
def after_request(response):
    #response.headers.add('Access-Control-Allow-Origin', f'chrome-extension://{EXTENTION_ID}')
    response.headers.add('Access-Control-Allow-Origin', 'https://www.google.com')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'append,delete,entries,foreach,get,has,keys,set,values,Authorization')
    response.headers.add('Access-Control-Allow-Headers', "X-Requested-With, Origin, X-Csrftoken, Content-Type, Accept")
    return response

@app.route('/', methods=['POST'])
def accsess_home():
    return 'home'

@app.route('/queue', methods=["POST"])
def add_urls():
    print(request.headers)
    urls = list()
    for _, url in request.json:
        urls.append(url)

    with open('./statics/queue', 'a') as queue:
        queue.write('\n'.join(urls))

    response_header = {
        'Vary': 'origin'
    }
    response_body = {
        'write': True
    }

    return Response(
        json.dump(response_body), 
        headers=response_header, 
        status=200
    )

@app.route('/analyze', methods=["POST"])
def analyze_url():
    target = request.json['url']


@app.route('/dump', methods=['GET'])
def get_dumpfle():
    return 'dumpfile'

if __name__ == '__main__':
    app.run(debug=True)
