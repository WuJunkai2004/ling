# ling
灵犀摘的后端

### Build
using pyvenv
```bash
```

### Develop
```bash
```

### Folder Structure
```bash
ling - backend branch
```

### vercel.py 的使用方法
#### 简单介绍
vercel.py 是一个类似nginx的python实现，主要用于处理请求和响应。  
verapi.py 是一个大量参考了vercel的api部署的python实现。调用 vercel.py, 并进行了数据处理和请求响应的封装。  
开启服务器的方法如下
```bash
./start.sh
```
在不同情况下，服务器会用不同的方式处理请求和响应。
- 当请求的路径是一个非python脚本时，服务器会直接返回该文件。
- 当请求的路径是一个python脚本时，服务器会拒绝返回该文件，并返回一个503错误。
- 当请求的路径是一个文件夹时，服务器会返回该文件夹下的index.html或者index.htm或者直接返回文件夹的目录。
- 当请求的路径加上 '.py' 是一个python脚本时，服务器将路径视为一个api，执行该脚本，并返回执行结果。

#### api的编写方法
api首先是一个python脚本，里面必须有一个函数被注册为入口。  
使用`@vercel.register`装饰器注册该函数为入口函数。  
该函数的名称可以自定义，但必须是一个合法的python函数名称。  
函数的四个参数(`response, url, data, headers`)都不是必须的。运行时会由环境自动传入。  
但是依然建议在函数定义时添加这四个参数，以便于调试和测试。
```python
import vercel

@vercel.register
def handler(response, url, data, headers):
    pass
```
函数的参数解释如下
- response: 请求的响应对象, 使用该对象返回响应
- url: 请求的url, 指向请求的路径，api通常不理会该参数
- data: 请求的body, 是一个json格式的字典，前端用request如何发送，后端就如何接收，无论是用post(json), post(form), get, get(param)何种方式发送，都能接收到同样的字典
- headers: 请求的头部, 是一个字典，api通常不理会该参数

#### api的响应
使用两种方式进行返回
##### 1.response返回
- status_code: 响应的状态码, 使用 response.send_code 函数返回。只能调用一次。
- headers: 响应的头部
> 使用 response.send_headers 函数返回，该函数需要传入一个字典，字典的key是头部的名称，value是头部的值。  
> 使用 response.send_header 函数返回，该函数需要传入一个头部的名称和头部的值。
- body: 响应的body
> 使用 response.send_text 函数返回，该函数需要传入一个字符串，作为响应的body。  
> 使用 response.send_file 函数返回，该函数需要传入一个文件的路径，作为响应的body。  
> 使用 response.send_json 函数返回，该函数需要传入一个字典，作为响应的body。

例子 1
```python
# 用text返回hello world
import vercel
@vercel.register
def text_handler(response):
    response.send_code(200)
    response.send_headers({
        'Content-Type': 'text/plain'
    })
    response.send_text('Hello World')
```
例子 2
```python
# 返回一个文件
import vercel
@vercel.register
def file_handler(response):
    response.send_code(200)
    response.send_header('Content-Type','text/html')
    response.send_file('index.html')
```
例子 3
```python
# 返回一个json
import vercel
@vercel.register
def json_handler(response, url):
    print(url)
    response.send_code(200)
    response.send_header('Content-Type','application/json')
    response.send_json({
        'name': 'lingxizau',
        'status': 'ok'
    })
```

##### 2.使用错误提示返回
```python
import vercel

@vercel.register
def error_handler(response):
    return vercel.ErrorStatu(response, 500)
```
ErrorStatu是一个服务器错误提示类，可以直接进行一个快速的错误响应。
它有三个参数，两个是必须的，一个是可选的
- response: 请求的响应对象, 使用该对象返回响应
- status_code: 响应的状态码。
- message: 响应的错误提示, 如果状态码是合法状态码时，可以不填，会自动生成。