from http.server import BaseHTTPRequestHandler
import json
import os

# Intentamos importar supabase, si falla devolvemos error visible
try:
    from supabase import create_client
    supabase_lib_ok = True
except Exception as e:
    supabase_lib_ok = False
    import_error = str(e)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')

        if not supabase_lib_ok:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"data": {}, "ok": True, "debug_import": import_error}).encode())
            return

        try:
            url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY')

            # Sacar user_id de la URL?user_id=...
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            user_id = query.get('user_id', [None])[0]

            if not url or not key:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"data": {}, "ok": True}).encode())
                return

            supabase = create_client(url, key)
            result = supabase.table('negocio_data').select('data').eq('user_id', user_id).execute()

            data = {}
            if result.data and len(result.data) > 0:
                data = result.data[0].get('data', {})

            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"data": data, "ok": True}).encode())

        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"data": {}, "ok": True, "error": str(e)}).encode())

    def do_POST(self):
        self.do_GET()
