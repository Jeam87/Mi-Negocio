from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def send(self, obj, code=200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            user_id = (qs.get('user_id', [None])[0] or qs.get('email', [None])[0] or '').strip().lower()
            if not user_id: return self.send({'ok': False, 'msg': 'falta user_id'}, 400)
            url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
            key = (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
            if not url or not key: return self.send({'ok': False, 'msg': 'Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Vercel'}, 500)
            full = f"{url}/rest/v1/negocio_data?user_id=eq.{urllib.parse.quote(user_id, safe='')}&select=data"
            req = urllib.request.Request(full, method='GET')
            req.add_header('apikey', key); req.add_header('Authorization', 'Bearer ' + key)
            with urllib.request.urlopen(req, timeout=20) as r:
                rows = json.loads(r.read().decode() or '[]')
            data = {}
            for row in rows:
                val = row.get('data') or {}
                if isinstance(val, str):
                    try: val = json.loads(val)
                    except Exception: val = {}
                if isinstance(val, dict): data.update(val)
            # Normalizar claves del inventario de materias primas para que no haya una copia vacía ocultando la otra.
            specific = next((v for k, v in data.items() if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt' and isinstance(v, (list, str))), None)
            general = data.get('inventarioMaestro')
            def as_list(v):
                if isinstance(v, str):
                    try: v = json.loads(v or '[]')
                    except Exception: return None
                return v if isinstance(v, list) else None
            a, b = as_list(specific), as_list(general)
            chosen = a if a is not None and len(a) else b if b is not None and len(b) else a if a is not None else b
            if chosen is not None:
                data['inventarioMaestro'] = chosen
                for k in list(data):
                    if k.startswith('inventarioMaestro_') and k != 'inventarioMaestro_updatedAt': data[k] = chosen
            return self.send({'ok': True, 'data': data, 'user_id': user_id})
        except Exception as e:
            return self.send({'ok': False, 'msg': str(e)}, 500)
