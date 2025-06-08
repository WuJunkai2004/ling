import vercel
import requests
import random
import json
import hashlib

trans_url: str = "http://api.fanyi.baidu.com/api/trans/vip/translate"
appid = '20250602002372171'
appkey = 'tTwWnkfrs8HUcuA_c6M6'


def make_md5(s, encoding='utf-8'):
    return hashlib.md5(s.encode(encoding)).hexdigest()


def translate(text):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + text + str(salt) + appkey)
    payload = {
        'appid': appid,
        'q': text,
        'from': 'en',
        'to': 'zh',
        'salt': salt,
        'sign': sign
    }
    try:
        response = requests.post(trans_url, params=payload, headers=headers)
    except Exception as e:
        print("error in post")
        print(e)
        return ''
    if response.status_code != 200:
        print("error in status code")
        return ''
    try:
        result = response.json()
    except:
        print("error in json")
        return ''
    ret = ''
    for i in result['trans_result']:
        ret += i['dst']
    return ret


def reply(response, success, text):
    print(f"text = {text}")
    response.send_code(200)
    response.send_json({
        "success": success,
        "text": text
    })
    

@vercel.register
def handler(response: vercel.API, data):
    """
    translate text using google translate api
    should get a data like
    {
        "token": "document_token",
        "text": "text to translate"
    }
    and return a json with the translated text
    """
    if response.method != "POST":
        return reply(response, False, "Method not allowed")
    if not data or "token" not in data or "text" not in data:
        return reply(response, False, "Invalid data")
    return reply(response, True, translate(data["text"]))
