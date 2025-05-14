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
def handler(response: vercel.API, url, data, headers):
    """
    Handles the POST request to upload a PDF file.
    """
    # Check if the request method is POST
    if response.method != 'POST':
        return vercel.ErrorStatu(response, 405)
    if len(data) != 1:
        return vercel.ErrorStatu(response, 400)

    file = data[0]
    md5  = get_md5(file['Content'])
    db   = dblite.SQL('./var/datas.db')
    find = db['files']['md5'].index(md5)
    if find == -1:
        file["Content"].seek(0)
        # 拼接对应的后缀名
        path = os.path.join('./var/files', md5 + os.path.splitext(file['filename'])[1])
        with open(path, 'wb') as f:
            response.copyfile(file['Content'], f)
        # 记录文件信息
        db['files'].insert(file['filename'],
                        md5 + os.path.splitext(file['filename'])[1],
                        md5,
        )
        file_info = md5 + os.path.splitext(file['filename'])[1]
    else:
        file_info = db['files']['filename'][find]

    response.send_code(200)
    response.send_headers({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    })
    response.send_text(json.dumps({
        'filename': file_info,
        'md5': md5,
        'token': md5,
    }))
    db.close()
    return
