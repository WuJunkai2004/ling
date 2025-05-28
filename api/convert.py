import subprocess
import vercel
import os


@vercel.register
def convert(response: vercel.API, data):
    """
    Handles the POST request to convert a PDF file to images.
    """
    # Check if the request method is POST
    if response.method != 'POST':
        return vercel.ErrorStatu(response, 405)
    if not os.path.exists('./var/html/' + data['token'] + '.html'):
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