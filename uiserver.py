from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import parse_qs
import cgi

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.hasSentResponse = False
        if callback is not None:
            queryStart = self.path.find('?')
            if queryStart > -1:
                parameters = parse_qs(self.path[queryStart+1:])
            else:
                parameters = {}
            self.invokeCallback(parameters)
        if not self.hasSentResponse:
            self.sendResponse(content)
    
    def do_POST(self):
        self.hasSentResponse = False
        parameters = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type']})
        self.invokeCallback(parameters)
        if not self.hasSentResponse:
            self.sendResponse(content)

    def log_message(self, format, *args):
        return
    
    def invokeCallback(self, parameters):
        path = self.path
        if '?' in path:
            path = path[:path.find('?')]
        if path in callback:
            callback[path](parameters, self)
    
    def sendResponse(self, response, type="text/html"):
        self.hasSentResponse = True
        self.send_response(200)
        self.send_header("Content-type", type)
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def sendDownload(self, download, filename):
        self.hasSentResponse = True
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", str(len(download)))
        self.send_header("Content-Disposition", 'attachment; filename="%s"' % filename)
        self.end_headers()
        self.wfile.write(download)

class _ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

content = ""
callback = {}
server = _ThreadingHTTPServer(("localhost", 8000), _Handler)

def beginServing():
    Thread(target=server.serve_forever).start()

def setContent(newContent):
    global content
    content = newContent

def setCallback(newCallback, path="/"):
    global callback
    callback[path] = newCallback
