import vercel
import requests
import dblite


def load_history(token):
    db = dblite.SQL('./var/datas.db')
    if not db[token].existed():
        db[token].create("question", "answer")
        db[token].commit()
    lens = len(db[token])
    result = []
    for i in range(max(lens - 5, 1), lens + 1):
        question = db[token]['question'][i]
        answer   = db[token]['answer'][i]
        result.append({
            "role": "user",
            "content": question
        })
        result.append({
            "role": "assistant",
            "content": answer
        })
    db.close()
    return result


def quest(question, token):
    api_key = "sk-b278fb2336e74e5e99069e6c5845d877"
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    content = []
    content.append({
        "role": "system",
        "content": "You are a helpful assistant."
    })
    content.extend(load_history(token))
    content.append({
        "role": "user",
        "content": question
    })
    payload = {
        "model": "qwen-turbo",
        "messages": content,
    }
    try:
        req = requests.post(api_url,
                            headers = headers,
                            json    = payload,
                            timeout = 10)
        req = req.json()
    except:
        return {
            "success": False,
            "response": {}
        }
    return {
        "success": True,
        "response": req
    }


def failed_response(response, code):
    response.set_status_code(200)
    response.send_json({
        "success": False,
        "answer": "",
        "message": f"Failed to process the request. The status code is {code}"
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
    if not result["success"] or not result["response"]["choices"]:
        return failed_response(response, 500)
    answer = result["response"]["choices"][0]["message"]["content"]
    db = dblite.SQL('./var/datas.db')
    db[token].insert(data["msg"], answer)
    db.close()
    response.send_code(200)
    response.send_json({
        "success": True,
        "answer": answer,
        "message": "Success"
    })
    