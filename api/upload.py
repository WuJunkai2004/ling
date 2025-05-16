import hashlib
import io
import json
import os
import dblite
import vercel
from langchain_community.document_loaders import PyMuPDFLoader

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

    pdf_path = os.path.join('.', 'var', 'files', file_info)
    loader = PyMuPDFLoader(pdf_path)
    pdf_pages = loader.load()
    import re
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    # 知识库中单段文本长度
    CHUNK_SIZE = 500

    # 知识库中相邻文本重合长度
    OVERLAP_SIZE = 50
    for pdf_page in pdf_pages:
        pattern = re.compile(r'[^\u4e00-\u9fff](\n)[^\u4e00-\u9fff]', re.DOTALL)
        pdf_page.page_content = re.sub(pattern, lambda match: match.group(0).replace('\n', ''), pdf_page.page_content)

    from langchain_community.embeddings import DashScopeEmbeddings

    embedding = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key="sk-b278fb2336e74e5e99069e6c5845d877"
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=OVERLAP_SIZE
    )
    split_docs = text_splitter.split_documents(pdf_pages)
    persist_directory = './var/vector_db'
    from langchain_community.vectorstores import Chroma
    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory=persist_directory  # 允许我们将persist_directory目录保存到磁盘上
    )

    print("done")


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
