from http.server import BaseHTTPRequestHandler
import json, os
from urllib.parse import urlparse, parse_qs

try:
    from supabase import create_client
    has_sb = True
except:
    has_sb = False

class handler(BaseHTTPRequestHandler):
    def send(self, obj, code=200):
        self.send_response(code)
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

    def get_client(self):
        # Lee cualquiera de los dos nombres
        url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
        key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_SECRET_KEY')
        if not has_sb or not url or not key:
            return None, f"url={bool(url)} key={bool(key)} has_sb={has_sb}"
        return create_client(url, key), None

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        user_id = qs.get('user_id',[None])[0] or qs.get('email',[None])[0] or qs.get('id',[None])[0] or "esaul_1987@hotmail.com"
        user_id = user_id.strip().lower()

        sb, err = self.get_client()
        data = {}
        if sb:
            try:
                r = sb.table('negocio_data').select('data').eq('user_id', user_id).execute()
                if r.data:
                    data = r.data[0].get('data',{}) or {}
            except Exception as e:
                err = str(e)

        return self.send({"ok":True, "data":data, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id, "debug":err})

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length else "{}"
        try: body = json.loads(raw)
        except: body = {}
        user_id = (body.get('user_id') or body.get('email') or body.get('id') or "esaul_1987@hotmail.com").strip().lower()
        data = body.get('data',{}) or {}

        sb, err = self.get_client()
        if sb:
            try:
                sb.table('negocio_data').upsert({"user_id":user_id, "data":data}, on_conflict="user_id").execute()
            except Exception as e:
                err = str(e)

        return self.send({"ok":True, "registered":True, "data":data, "user_id":user_id, "id":user_id, "email":user_id, "identifier":user_id, "debug":err})
