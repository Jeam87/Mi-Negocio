from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length else "{}"
        try: body = json.loads(raw)
        except: body = {}
        user_id = (body.get('user_id') or body.get('negocio_id') or "esaul_1987@hotmail.com").lower()
        data = body.get('data') or {}
        url = (os.environ.get('SUPABASE_URL') or "").strip().rstrip('/')
        key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or "").strip()
        if url and key:
            try:
                full = f"{url}/rest/v1/negocio_data"
                payload = json.dumps({"user_id": user_id, "data": data}).encode()
                req = urllib.request.Request(full, data=payload, method='POST')
                req.add_header('apikey', key)
                req.add_header('Authorization', f'Bearer {key}')
                req.add_header('Content-Type', 'application/json')
                req.add_header('Prefer', 'resolution=merge-duplicates')
                urllib.request.urlopen(req, timeout=8).read()
            except: pass
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"ok":True}).encode())
