import hashlib
import io
import json
import os
import dblite
import vercel
from langchain_community.document_loaders import PyMuPDFLoader
import threading
from langchain_community.embeddings import DashScopeEmbeddings
from config import DASHSCOPE_API_KEY, EMBEDDING_MODEL
from pydantic import BaseModel, Field

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


class ArticleResults(BaseModel):
    abstract:str = Field(description="Brief summary of the article's abstract")
    key_findings:str = Field(description="The key findings of the article")
    limitation_of_sota : str=Field(description="limitation of the existing work")
    proposed_solution : str = Field(description="the proposed solution in details")
    paper_limitations : str=Field(description="The limitations of the proposed solution of the paper")


def process_pdf_to_vector(pdf_path):
    """异步处理PDF文件并构建向量数据库"""
    try:
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



        embedding = DashScopeEmbeddings(
            model=EMBEDDING_MODEL,
            dashscope_api_key=DASHSCOPE_API_KEY
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
            persist_directory=persist_directory
        )
        print("Vector database construction completed")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")


def increase_build_rag(pdf_path):
    """增加RAG构建任务"""
    from itext2kg import iText2KG
    from langchain.document_loaders import PyPDFLoader
    from itext2kg.documents_distiller import DocumentsDistiller
    from langchain_community.chat_models import ChatTongyi
    from langchain_community.embeddings import ZhipuAIEmbeddings

    print("load llm...")
    llm_api_key = "sk-b278fb2336e74e5e99069e6c5845d877"
    embeddings_api_key = "9004d12880604aa189d7a946c9e248af.9XnbjH4aHoR5ew0G"
    llm = ChatTongyi(
        api_key = llm_api_key,
        model="qwen-turbo",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    embeddings = ZhipuAIEmbeddings(
        api_key = embeddings_api_key,
        model="embedding-3",
    )
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    document_distiller = DocumentsDistiller(llm_model=llm)
    document_type = 'scientific article'
    IE_query = f'''
    # DIRECTIVES : 
    - Act like an experienced information extractor.
    - You have a chunk of a {document_type}
    - If you do not find the right information, keep its place empty.
    '''
    # Distill document content with query
    distilled_doc = document_distiller.distill(
        documents=[page.page_content.replace("{", '[').replace("}", "]") for page in pages],
        IE_query=IE_query,
        output_data_structure=ArticleResults
    )
    distilled_docs = [
        f"{document_type}'s {key} - {value}".replace("{", "[").replace("}", "]") 
        for key, value in distilled_doc.items() 
        if value and value != []
    ]
    itext2kg = iText2KG(llm_model = llm, embeddings_model = embeddings)
    kg_loaded = itext2kg.load_graph("llm-tikg.json")
    kg_incres = itext2kg.build_graph(sections=distilled_docs,
                         existing_knowledge_graph=kg_loaded,
                         rel_threshold=0.7, ent_threshold=0.7)
    itext2kg.save_graph(kg_incres, "llm-tikg.json")


@vercel.register
def handler(response: vercel.API, url, data, headers):
    """处理PDF文件上传请求"""
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
        path = os.path.join('./var/files', md5 + os.path.splitext(file['filename'])[1])
        with open(path, 'wb') as f:
            response.copyfile(file['Content'], f)
        db['files'].insert(file['filename'],
                        md5 + os.path.splitext(file['filename'])[1],
                        md5,
        )
        file_info = md5 + os.path.splitext(file['filename'])[1]
    else:
        file_info = db['files']['filename'][find]

    # 启动异步处理
    pdf_path = os.path.join('.', 'var', 'files', file_info)
    thread = threading.Thread(target=increase_build_rag, args=(pdf_path,))
    thread.daemon = True  # 设置为守护线程
    thread.start()

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
