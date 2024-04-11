from flask import Flask, request, jsonify, Response
import json
import requests

app = Flask(__name__)
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
    return jsonify(response.json()), response.status_code


def chk_keys():
    print("Checking keys")


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


if __name__ == '__main__':
    get_auth()
    if not USER_AUTH:
        print('No auth file found')
    else:
        # json user auth to string
        auths = json.dumps(USER_AUTH)
        print(f'Auth file found: {auths}')
    app.run(host="0.0.0.0", port=5980)