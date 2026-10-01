from http.server import BaseHTTPRequestHandler
import json, os
from urllib.parse import urlparse, parse_qs

try:
    from supabase import create_client
    has_sb = True
except:
    has_sb = False

class handler(BaseHTTPRequestHandler):
    def send(self, obj):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        user_id = qs.get('user_id',[None])[0] or qs.get('email',[None])[0] or qs.get('id',[None])[0]
        if not user_id:
            user_id = "esaul_1987@hotmail.com"
        try:
            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
            data = {}
            if has_sb and url and key:
                sb = create_client(url, key)
                r = sb.table('negocio_data').select('data').eq('user_id', user_id).execute()
                if r.data:
                    data = r.data[0].get('data',{})
            # Devolvemos el identificador en TODOS los nombres posibles
            return self.send({"ok":True, "data":data, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id})
        except Exception as e:
            return self.send({"ok":True, "data":{}, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id, "warn":str(e)})

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length else "{}"
        try:
            body = json.loads(raw)
        except:
            body = {}
        user_id = body.get('user_id') or body.get('email') or body.get('id') or "esaul_1987@hotmail.com"
        data = body.get('data',{})

        try:
            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
            if has_sb and url and key:
                sb = create_client(url, key)
                # asegurar que existe
                sb.table('negocio_data').upsert({"user_id":user_id, "data":data or {}}).execute()
        except Exception as e:
            pass

        return self.send({"ok":True, "registered":True, "data":data or {}, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id})
