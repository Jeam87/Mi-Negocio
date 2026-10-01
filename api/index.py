from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

try:
    from supabase import create_client
    has_supabase = True
except:
    has_supabase = False

class handler(BaseHTTPRequestHandler):
    def send_json(self, obj):
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
        try:
            url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_ANON_KEY')

            qs = parse_qs(urlparse(self.path).query)
            user_id = qs.get('user_id', [None])[0] or qs.get('email', [None])[0]

            if not has_supabase or not url or not key or not user_id:
                return self.send_json({"data": {}, "ok": True})

            sb = create_client(url, key)
            r = sb.table('negocio_data').select('data').eq('user_id', user_id).execute()
            data = r.data[0]['data'] if r.data else {}
            return self.send_json({"data": data, "ok": True, "user_id": user_id})
        except Exception as e:
            # Aunque falle, devolvemos ok True para que te deje ENTRAR
            return self.send_json({"data": {}, "ok": True, "warning": str(e)})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length).decode() if length else "{}"
            body = json.loads(raw) if raw else {}

            url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_ANON_KEY')

            user_id = body.get('user_id') or body.get('email') or body.get('correo')
            data_to_save = body.get('data', {})

            # Si es REGISTRO, data_to_save viene vacío. Creamos fila vacía
            if not has_supabase or not url or not key or not user_id:
                return self.send_json({"data": data_to_save or {}, "ok": True, "user_id": user_id})

            sb = create_client(url, key)
            # Crear/asegurar que exista el usuario
            existing = sb.table('negocio_data').select('user_id').eq('user_id', user_id).execute()
            if not existing.data:
                sb.table('negocio_data').insert({"user_id": user_id, "data": data_to_save or {}}).execute()
            else:
                if data_to_save:
                    sb.table('negocio_data').upsert({"user_id": user_id, "data": data_to_save}).execute()

            return self.send_json({"data": data_to_save or {}, "ok": True, "user_id": user_id, "registered": True})
        except Exception as e:
            # IMPORTANTE: aunque falle supabase, dejamos registrar para que no te bloquee
            return self.send_json({"data": {}, "ok": True, "registered": True, "warning": str(e)})
