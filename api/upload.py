import vercel

@vercel.register
def handler(self: vercel.API, url, data, headers):
    """
    Handles the POST request to upload a PDF file.
    
    Args:
        self: The Vercel request object.
        url: The URL to which the request is sent.
        headers: The headers for the request.
        data: The data to be sent in the request.
    
    Returns:
        A JSON response with the status and message.
    """
    # Check if the request method is POST
    if self.method != 'POST':
        return vercel.ErrorStatu(self, 405)

    # Check if the content type is multipart/form-data
    print(data)
    for file in data:
        if not file['Content']:
            continue
        # file['Content'] is the BytesIO object
        # save it to test.pdf
        with open('test.txt', 'wb') as f:
            f.write(file['Content'].read())
    vercel.ErrorStatu(self, 200)