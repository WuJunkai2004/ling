import vercel
import requests
import dblite

import os
import requests
import json

API_URL = "https://api.gitcode.com/api/v5/chat/completions"
headers = {
    "Authorization": f"Bearer dZ_1jQfsohYYyqUCkWWCiQN4",
}

def query(payload):
    print("call query")
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return "Error: " + result.get("message", "Unknown error")

def load_history(token):
    db = dblite.SQL('./var/datas.db')
    if not db[token].existed():
        db[token].create("question", "answer")
        db[token].commit()
    lens = len(db[token])
    result = []

    for i in range(max(lens - 20, 1), lens + 1):
        question = db[token]['question'][i]
        result.append({
            "role": "user",
            "content": question
        })
    print(f"histrory{result}")

    db.close()
    return result


def quest(question, token):
    content = []
    content.append({
        "role": "system",
        "content": "You are a helpful assistant. Please always respond in Chinese (简体中文)."
    })
    content.extend(load_history(token))
    content.append({
        "role": "user",
        "content": question
    })

    # 创建一个新的消息数组
    messages = []
    messages.append({
        "role": "system",
        "content": f"这是用户的历史对话记录：{str(content)}"
    })
    messages.append({
        "role": "user",
        "content": f"根据以上历史记录，请回答问题：{question}"
    })
    
    payload = {
        "messages": messages,
        "model": "deepseek-ai/DeepSeek-V3.2",
        "stream": False
    }
    req = query(payload)
    print(f"Request to DashScope API: {req}")
    print("will return")
    return {
        "success": True,
        "response": req
    }


def failed_response(response, code):
    print(f"Failed to process the request. The status code is {code}")
    response.send_code(200)
    response.send_json({
        "success": False,
        "answer": "",
        "message": f"Failed to process the request. The status code is {code}",
        "msg": f"Failed to process the request. The status code is {code}"
    })


@vercel.register
def chat(response: vercel.API, data):
    """
    data should be a dict like this
    {
        msg: what is the mean of selection,
        selection: {the selection of the paragraph},
        token: {the token of the file},
    }

    and return a dict like this
    {
        success: True
        answer: {the answer of the question}
        message: {the message of the request}
    }
    """
    if "msg" not in data or "selection" not in data or "token" not in data:
        return failed_response(response, 400)
    if not data["selection"]:
        question = f"""
please answer the question:
```
{data['msg']}
```
"""
    else:
        question = f"""
the selection is
```
{data['selection']}
```

please answer the question:
```
{data['msg']}
```
"""
    token = data["token"]
    result = quest(question, token)
    print(f"quest result: {result}")
    if not result["success"] or not result["response"]:
        return failed_response(response, 500)
    answer = result["response"]
    db = dblite.SQL('./var/datas.db')
    db[token].insert(data["msg"], answer)
    db.close()
    response.send_code(200)
    response.send_json({
        "success": True,
        "answer": answer,
        "message": "Success"
    })
