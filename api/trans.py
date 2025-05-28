import vercel

def reply(response, success, text):
    response.send_code(200)
    response.send_json({
        "success": success,
        "text": text
    })
    

@vercel.register
def handler(response, data):
    """
    translate text using google translate api
    should get a data like
    {
        "token": "document_token",
        "text": "text to translate"
    }
    and return a json with the translated text
    """
    if response.method != "POST":
        return reply(response, False, "Method not allowed")
    if not data or "token" not in data or "text" not in data:
        return reply(response, False, "Invalid data")
    pass
