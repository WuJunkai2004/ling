from imp  import load_source

import os
import vercel

def main(handler = vercel.API, port = 8000):
    vercel.start(
        HandlerClass = handler,
        port = port
    )


class handler(vercel.API):
    def vercel(self, url, data, headers):
        if(os.path.isdir(url)):
            self.send_code(200)
            for home in ['index.html','index.htm']:
                if(os.path.isfile(url + home)):
                    self.send_file(url + home)
                    return
            self.send_text( '\n'.join(os.listdir(url)) )
            return
    
        if(os.path.isfile(url)):
            if(os.path.splitext(url)[1]=='.py'):
                return vercel.ErrorStatu(self, 403)
            self.send_code(200)
            self.send_file(url)
            return

        if(os.path.isfile(url + '.py')):
            mod = load_source(url,url + '.py')
            try:
                mod.handler.vercel(self, url, data, headers)
            except AttributeError:
                vercel.ErrorStatu(self, 503)
            return
        
        vercel.ErrorStatu(self, 404)


if(__name__=='__main__'):
    main( handler )