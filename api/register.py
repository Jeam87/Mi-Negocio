from http.server import BaseHTTPRequestHandler
import json
class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length else "{}"
        try: body = json.loads(raw)
        except: body = {}
        email = (body.get('email') or body.get('user_id') or "").strip().lower()
        if not email:
            email = "esaul_1987@hotmail.com"
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        resp = {"ok": True, "negocio_id": email, "user_id": email, "id": email, "email": email, "identifier": email}
        self.wfile.write(json.dumps(resp).encode())
