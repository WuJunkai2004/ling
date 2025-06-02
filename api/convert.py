import subprocess
import vercel
import os
import fitz


def prepare_pdf(token):
    # 检查 PDF 文件是否存在
    if os.path.exists('./var/files/' + token + '.pdf'):
        return True
    # 若pdf文件不存在，检查是否存在 caj 文件
    if not os.path.exists('./var/files/' + token + '.caj'):
        return False
    # 若 caj 文件存在，转换为 PDF
    cmd = [
        'caj2pdf',
        '--input', './var/files/' + token + '.caj',
        '--output', './var/files/' + token + '.pdf'
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        return False
    return True


def prepare_cover(token):
    # 检查封面图片是否存在
    if os.path.exists('./var/html/' + token + '.png'):
        return True
    # 若封面图片不存在，生成封面
    pdf_path = './var/files/' + token + '.pdf'
    # 宽度最多为 240
    pdf_docs = fitz.open(pdf_path)
    if pdf_docs.page_count == 0:
        return False
    pdf_page = pdf_docs[0]
    # 获取页面的宽度和高度
    width = pdf_page.rect.width
    height = pdf_page.rect.height
    need_rotate = width < height
    if need_rotate:
        width, height = height, width
    # 计算缩放比例
    scale = 240 / width
    # 生成封面图片
    pix = pdf_page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    pix.save('./var/cover/' + token + '.png')


@vercel.register
def convert(response: vercel.API, data):
    """
    Handles the POST request to convert a PDF file to images.
    """
    # Check if the request method is POST
    if response.method != 'POST':
        return vercel.ErrorStatu(response, 405)
    if not os.path.exists('./var/html/' + data['token'] + '.html'):
        if not prepare_pdf(data['token']):
            return vercel.ErrorStatu(response, 500)
        prepare_cover(data['token'])
        cmd = [
            'pdf2htmlEX',
            '--fit-width', '800',
            '--process-outline', '0',
            './var/files/' + data['token'] + '.pdf',
            './var/html/' + data['token'] + '.html',
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return vercel.ErrorStatu(response, 500)
    # Send the response
    response.send_code(200)
    response.send_headers({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    })
    response.send_json({'status': 'success'})