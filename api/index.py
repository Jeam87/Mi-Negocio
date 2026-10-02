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

    def get_env(self):
        url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or ''
        key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or ''
        url = url.strip().rstrip('/')
        return url, key

    def sb_request(self, method, path, body=None):
        url, key = self.get_env()
        if not url or not key:
            return None, "Faltan SUPABASE_URL o SERVICE_ROLE_KEY"
        full = f"{url}/rest/v1/{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(full, data=data, method=method)
        req.add_header('apikey', key)
        req.add_header('Authorization', f'Bearer {key}')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Prefer', 'resolution=merge-duplicates')
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt else {}, None
        except urllib.error.HTTPError as e:
            txt = e.read().decode()
            # Si no hay datos es normal, no es error
            if e.code == 406 or "0 rows" in txt:
                return [], None
            return None, f"{e.code} {txt[:300]}"
        except Exception as e:
            return None, str(e)

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        user_id = (qs.get('user_id',[None])[0] or qs.get('email',[None])[0] or qs.get('id',[None])[0] or "esaul_1987@hotmail.com").strip().lower()

        result, err = self.sb_request('GET', f"negocio_data?user_id=eq.{urllib.parse.quote(user_id)}&select=data")
        data = {}
        if result and len(result)>0:
            data = result[0].get('data',{}) or {}

        return self.send({"ok":True, "data":data, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id, "debug":err})

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length else "{}"
        try: body = json.loads(raw)
        except: body = {}
        user_id = (body.get('user_id') or body.get('email') or body.get('id') or "esaul_1987@hotmail.com").strip().lower()
        data = body.get('data',{}) or {}

        # upsert
        self.sb_request('POST', 'negocio_data', {"user_id": user_id, "data": data})

        return self.send({"ok":True, "registered":True, "data":data, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id})
