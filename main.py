# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import json
from flask import Flask, request, jsonify, make_response

from google.cloud import datastore

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/apiai', methods=['POST'])
def handle():
    req = request.get_json(silent=True, force=True)
    print 'Request:'
    print(json.dumps(req, indent=4))
    if req.get('queryResult').get('action') != 'lookup':
        return {}
    topic = req.get('queryResult').get('parameters').get('topic')
    print topic
    rsp = getResponse(topic)
    rsp = json.dumps(rsp, indent=4)
    print rsp
    r = make_response(rsp)
    r.headers['Content-Type'] = 'application/json'
    return r

def getResponse(topic):
    
    client = datastore.Client()
    query = client.query(kind='Synonym')
    key = client.key('Synonym', topic)
    query.key_filter(key, '=')
    results = list(query.fetch())
    
    if len(results) == 0:
        return buildReply('I can\'t find that in the handbook...')
    
    print results[0]['synonym']
    
    query = client.query(kind='Topic')
    key = client.key('Topic', results[0]['synonym'])
    query.key_filter(key, '=')
    results = list(query.fetch())
    
    print results[0]['action_text']
    
    return buildReply(results[0]['action_text'])

def buildReply(info):
    return {
        'fulfillmentText': info,
        'source': 'apiai'
    }

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
