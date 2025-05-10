import subprocess
import vercel
import os


@vercel.register
def handler(self: vercel.API, url, data, headers):
    """
    Handles the POST request to convert a PDF file to images.
    """
    # Check if the request method is POST
    if self.method != 'POST':
        return vercel.ErrorStatu(self, 405)
    if not os.path.exists('./var/html/' + data['token'] + '.html'):
        cmd = [
            'pdf2htmlEX',
            '--fit-width', '800',
            './var/files/' + data['token'] + '.pdf',
            './var/html/' + data['token'] + '.html',
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return vercel.ErrorStatu(self, 500)
    # Send the response
    self.send_code(200)
    self.send_headers({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    })
    self.send_text('{"status": "success"}')