import vercel
import requests
import dblite
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_API_URL,
    EMBEDDING_MODEL,
    CHAT_MODEL
)

# 初始化 embedding 模型
embedding = DashScopeEmbeddings(
    model=EMBEDDING_MODEL,
    dashscope_api_key=DASHSCOPE_API_KEY
)

# 加载持久化的向量数据库
vectordb = Chroma(
    persist_directory='./var/vector_db',
    embedding_function=embedding
)

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
    print(result)

    db.close()
    return result


def quest(question, token):
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
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

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    messages.append({
        "role": "system",
        "content": f"这是检索到的内容：{str(docs)}"
    })
    
    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
    }
    try:
        req = requests.post(DASHSCOPE_API_URL,
                            headers=headers,
                            json=payload,
                            timeout=10)
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

    