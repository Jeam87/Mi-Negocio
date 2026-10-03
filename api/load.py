from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def send(self, obj, code=200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_OPTIONS(self):
        self.send({}, 200)

    def get_env(self):
        url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
        key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
        return url, key

    def sb(self, method, path, body=None):
        url, key = self.get_env()
        if not url or not key: return None
        full = f"{url}/rest/v1/{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(full, data=data, method=method)
        req.add_header('apikey', key)
        req.add_header('Authorization', f'Bearer {key}')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Prefer', 'resolution=merge-duplicates')
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt else []
        except:
            return []

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        user_id = (qs.get('user_id',[None])[0] or qs.get('email',[None])[0] or qs.get('negocio_id',[None])[0] or '').strip().lower()
        if not user_id:
            return self.send({"ok":False,"msg":"falta user_id"},400)
        arr = self.sb('GET', f"negocio_data?user_id=eq.{urllib.parse.quote(user_id)}&select=data")
        data = arr[0].get('data',{}) if arr else {}
        return self.send({"ok":True,"data":data,"user_id":user_id})

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get('Content-Length',0) or 0)).decode() or "{}"
        body = json.loads(raw) if raw else {}
        user_id = (body.get('user_id') or body.get('email') or body.get('id') or '').strip().lower()
        incoming = body.get('data') or {}
        if not user_id or not incoming:
            return self.send({"ok":False,"msg":"falta data"},400)

        # MERGE para no borrar agenda/entregas
        old_arr = self.sb('GET', f"negocio_data?user_id=eq.{urllib.parse.quote(user_id)}&select=data")
        old = old_arr[0].get('data',{}) if old_arr else {}
        merged = {**old, **incoming}

        self.sb('POST', 'negocio_data', {"user_id": user_id, "data": merged})
        return self.send({"ok":True,"data":merged})
