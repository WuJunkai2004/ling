import hashlib
import io
import json
import os

import dblite
import vercel

def get_md5(file_content: io.BytesIO) -> str:
    """
    Calculate the MD5 hash of the given file content. Just count the first 8k bytes.
    @ brief: file_content: A BytesIO object containing the file content.
    @ return: The MD5 hash of the file content as a hexadecimal string.
    """
    md5_hash = hashlib.md5()
    chuck = file_content.read(8192)
    md5_hash.update(chuck)
    return md5_hash.hexdigest()


@vercel.register
def handler(self: vercel.API, url, data, headers):
    """
    Handles the POST request to upload a PDF file.
    """
    # Check if the request method is POST
    if self.method != 'POST':
        return vercel.ErrorStatu(self, 405)
    if len(data) != 1:
        return vercel.ErrorStatu(self, 400)

    file = data[0]
    md5  = get_md5(file['Content'])
    db   = dblite.SQL('./var/datas.db')
    find = db['files']['md5'].index(md5)
    if find != -1:
        # File already exists, 
        # return the json with the file name and the md5 and file token
        file_info = db['files'][find]
        self.send_code(200)
        self.send_headers({
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        })
        self.send_text(json.dumps({
            'filename': file_info['filename'],
            'md5': md5,
            'token': md5,
        }))
        return
    file["Content"].seek(0)
    # 拼接对应的后缀名
    path = os.path.join('./var/files', md5 + os.path.splitext(file['filename'])[1])
    with open(path, 'wb') as f:
        self.copyfile(file['Content'], f)
    # 记录文件信息
    db['files'].insert({
        'filename': md5 + os.path.splitext(file['filename'])[1],
        'md5': md5,
    })
    db.commit()
    db.close()