from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

try:
    from supabase import create_client
    supabase_ok = True
except Exception as e:
    supabase_ok = False
    err_import = str(e)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if not supabase_ok:
            self.wfile.write(json.dumps({"data": {}, "ok": True, "debug": err_import}).encode())
            return

        try:
            url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY')

            query = parse_qs(urlparse(self.path).query)
            user_id = query.get('user_id', [None])[0]

            if not url or not key or not user_id:
                self.wfile.write(json.dumps({"data": {}, "ok": True}).encode())
                return

            sb = create_client(url, key)
            res = sb.table('negocio_data').select('data').eq('user_id', user_id).execute()

            d = {}
            if res.data and len(res.data) > 0:
                d = res.data[0].get('data', {})

            self.wfile.write(json.dumps({"data": d, "ok": True}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"data": {}, "ok": True, "error": str(e)}).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        try:
            body_json = json.loads(body)
        except:
            body_json = {}

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        try:
            url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY')
            user_id = body_json.get('user_id') or body_json.get('email')
            data_to_save = body_json.get('data', body_json)

            if not url or not key or not user_id:
                self.wfile.write(json.dumps({"ok": False, "error": "falta config"}).encode())
                return

            sb = create_client(url, key)
            sb.table('negocio_data').upsert({"user_id": user_id, "data": data_to_save}).execute()
            self.wfile.write(json.dumps({"ok": True, "data": data_to_save}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
