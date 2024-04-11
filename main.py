import time

from flask import Flask, request, jsonify, Response
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
scheduler = BackgroundScheduler(daemon=True)
USER_AUTH = []


def find_min_count_key(auth_file):
    with open(f'config/{auth_file}.json', 'r') as file:
        keys = json.load(file)
    if not keys:
        raise ValueError("no keys")
    min_count_key = min(keys, key=lambda obj: obj['count'])
    print(f'key: {min_count_key["key"]}, count: {min_count_key["count"]}')
    return min_count_key['key']


@app.route('/v2/translate', methods=['POST'])
@app.route('/translate', methods=['POST'])
def deep_l_translate():
    auth_header = request.headers.get('Authorization')
    # if not auth_header or USER_AUTH not in auth_header:
    #     return Response('Unauthorized', status=401)
    if not auth_header:
        return Response('Unauthorized', status=401)
    if ' ' not in auth_header:
        return Response('Unauthorized', status=401)
    chk_auth = auth_header.split(' ')[1]
    if chk_auth not in USER_AUTH:
        return Response('Unauthorized', status=401)

    try:
        min_count_key = find_min_count_key(chk_auth)
    except ValueError as e:
        return Response(str(e), status=401)

    url = 'https://api-free.deepl.com/v2/translate'
    headers = {
        'Authorization': f'DeepL-Auth-Key {min_count_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=request.json)
    if response.status_code == 200:
        return jsonify(response.json()), response.status_code
    else:
        return Response(f'Error {response.status_code} {response.text}', status=403)


@app.route('/v2/usage', methods=['GET'])
def chk_keys():
    print(f"{time.time()} Checking keys ")
    for auth_file in USER_AUTH:
        save_keys = []
        with open(f'config/{auth_file}.json', 'r') as file:
            keys = json.load(file)
        if not keys:
            print(f'No keys found in {auth_file}.json')
        else:
            for key in keys:
                url = 'https://api-free.deepl.com/v2/usage?auth_key=' + key["key"]
                response = requests.get(url)
                if response.status_code == 200:
                    key["count"] = response.json()["character_count"]
                    key["limit"] = response.json()["character_limit"]
                    save_keys.append(key)
                    print('response status: 200 OK')
                    print("response json: ", response.json())
                    print(f'key: {key["key"]}, count: {key["count"]}')
                else:
                    print(f'key: {key["key"]}, count: {key["count"]}, status: {response.status_code}')
                    save_keys.append(key)
            json.dump(save_keys, open(f'config/{auth_file}.json', 'w'), indent=4)
    return Response('OK', status=200)


# 添加 key，如果指定的 auth 文件不存在，则创建后添加，如果 key 已存在，则返回 201
@app.route('/v2/add', methods=['POST', 'GET'])
def add_key():
    key = ''
    new_auth_file_name = ''
    if request.method == 'POST':
        key = request.json.get('key')
        new_auth_file_name = request.json.get('auth')
    else:
        key = request.args.get('key')
        new_auth_file_name = request.args.get('auth')
    if not key:
        return Response('Key not found in request', status=400)

    if new_auth_file_name not in USER_AUTH:
        USER_AUTH.append(new_auth_file_name)
        list = []
        list.append({'key': key, 'count': 0})
        json.dump(list, open(f'config/{new_auth_file_name}.json', 'w'), indent=4)
        return Response('Auth file created and key added', status=200)

    with open(f'config/{new_auth_file_name}.json', 'r') as file:
        keys = json.load(file)
    if not keys:
        keys = []
    for k in keys:
        if k['key'] == key:
            return Response('Key already exists', status=201)
    keys.append({'key': key, 'count': 0})
    json.dump(keys, open(f'config/{new_auth_file_name}.json', 'w'), indent=4)
    return Response('Key added', status=200)



@app.route('/')
def hello_world():
    return 'Hello World!'


# 查询 config 文件夹下 所有 json 文件，并把文件名写入到 auth 数组中
def get_auth():
    import os
    path = 'config'
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.json'):
                USER_AUTH.append(file.split('.json')[0])


scheduler.add_job(func=chk_keys, trigger="interval", seconds=60*60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    get_auth()
    if not USER_AUTH:
        print('No auth file found')
    else:
        # json user auth to string
        auths = json.dumps(USER_AUTH)
        print(f'Auth file found: {auths}')
    app.run(host="0.0.0.0", port=5980)