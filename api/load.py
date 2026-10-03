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
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        user_id = (qs.get('user_id',[None])[0] or qs.get('email',[None])[0] or '').strip().lower()
        if not user_id:
            return self.send({"ok":True,"data":{}})
        url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
        key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
        data = {}
        if url and key:
            try:
                full = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id)}&select=data"
                req = urllib.request.Request(full, method='GET')
                req.add_header('apikey', key)
                req.add_header('Authorization', f'Bearer {key}')
                with urllib.request.urlopen(req, timeout=10) as r:
                    arr = json.loads(r.read().decode() or "[]")
                    if arr: data = arr[0].get('data',{}) or {}
            except Exception as e:
                pass
        return self.send({"ok":True,"data":data,"user_id":user_id})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length',0))
            raw = self.rfile.read(length).decode() if length else "{}"
            body = json.loads(raw or "{}")
            user_id = (body.get('user_id') or body.get('email') or '').strip().lower()
            incoming = body.get('data') or {}
            if not user_id:
                return self.send({"ok":False,"msg":"falta user_id"},400)

            url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
            key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
            # leer viejo
            old = {}
            try:
                full = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id)}&select=data"
                req = urllib.request.Request(full, method='GET')
                req.add_header('apikey', key)
                req.add_header('Authorization', f'Bearer {key}')
                with urllib.request.urlopen(req, timeout=10) as r:
                    arr = json.loads(r.read().decode() or "[]")
                    if arr: old = arr[0].get('data',{}) or {}
            except: pass

            merged = {**old, **incoming}
            # guardar
            try:
                full = f"{url}/rest/v1/negocio_data"
                req = urllib.request.Request(full, data=json.dumps({"user_id":user_id,"data":merged}).encode(), method='POST')
                req.add_header('apikey', key)
                req.add_header('Authorization', f'Bearer {key}')
                req.add_header('Content-Type', 'application/json')
                req.add_header('Prefer', 'resolution=merge-duplicates')
                with urllib.request.urlopen(req, timeout=10) as r:
                    r.read()
            except Exception as e:
                return self.send({"ok":False,"msg":str(e)},500)

            return self.send({"ok":True,"data":merged})
        except Exception as e:
            return self.send({"ok":False,"msg":str(e)},500)
