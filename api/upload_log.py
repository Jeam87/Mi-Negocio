from http.server import BaseHTTPRequestHandler
import json, os, base64
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            logo_b64 = data.get('logo', '')
            negocio_id = data.get('negocio_id', 'default')

            if ',' in logo_b64:
                logo_b64 = logo_b64.split(',', 1)[1]
            logo_bytes = base64.b64decode(logo_b64)

            SUPABASE_URL = os.environ.get('SUPABASE_URL')
            SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

            if not SUPABASE_URL or not SUPABASE_KEY:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "msg": "Falta config Supabase"}).encode())
                return

            path = f"{negocio_id}/logo.png"
            url_storage = f"{SUPABASE_URL}/storage/v1/object/logos/{path}"

            req = urllib.request.Request(url_storage, data=logo_bytes, method='POST')
            req.add_header('apikey', SUPABASE_KEY)
            req.add_header('Authorization', f'Bearer {SUPABASE_KEY}')
            req.add_header('Content-Type', 'image/png')
            req.add_header('x-upsert', 'true')
            try:
                urllib.request.urlopen(req)
            except:
                req2 = urllib.request.Request(url_storage, data=logo_bytes, method='PUT')
                req2.add_header('apikey', SUPABASE_KEY)
                req2.add_header('Authorization', f'Bearer {SUPABASE_KEY}')
                req2.add_header('Content-Type', 'image/png')
                req2.add_header('x-upsert', 'true')
                urllib.request.urlopen(req2)

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/logos/{path}"

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "url": public_url}).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "msg": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
