from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        html = "<h1>TIENDA FUNCIONANDO</h1><p>Si ves esto, ya jalo el rewrite</p>"
        self.wfile.write(html.encode())
