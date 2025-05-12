"""
通过token -> md5，快速确定文件是否存在
"""

import vercel
import dblite

@vercel.register
def handles(response: vercel.API, data):
    if 'token' not in data:
        response.send_code(400)
        response.send_json({
            "status": False
        })
        return
    md5 = data['token']
    db  = dblite.SQL('./var/datas.db')
    idx = db['files']['md5'].index(md5)
    if idx == -1:
        response.send_code(200)
        response.send_json({
            "status": False
        })
    else:
        response.send_code(200)
        response.send_json({
            "status": True
        })
    db.close()